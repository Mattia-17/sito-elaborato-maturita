#import
from flask import Flask, render_template, request, session, redirect, url_for, flash
import pymssql as p
from datetime import datetime

app = Flask(__name__)
#chiave segreta per il salvataggio di dati nella session
app.secret_key="chiavesegreta"

#settare la connessione al db
conn = p.connect(server='213.140.22.237', user='5DINFGALVANI2021ESAME', password='5DINFGALVANI2021ESAME', database='5DINFGALVANI2021ESAME')

#funzione pagina iniziale
@app.route('/', methods=['GET', 'POST'])
def index():  
    return render_template('index.html')

#funzione pagina di login
@app.route('/login', methods=['GET', 'POST'])
def login():
    erroreP = False
    erroreC = False
    erroreN = False
    erroreE = False
    #esecuzione del metodo post
    if request.method == "POST":
        #salvataggio i dati inviati dalla form
        nome = request.form["name"]
        cognome = request.form["surname"]
        email = request.form["email"]
        password = request.form["password"]
        #select di tutti i dati degli utenti salvati nella tabella BUON_PALESTRA
        cursor = conn.cursor()
        query = "SELECT * FROM BUON_UTENTE_PALESTRA"
        cursor.execute(query)
        utenti = cursor.fetchall()
        #stampare in console i dati ottenuti
        print(utenti)
        #controllo delle credenziali inserite dall'utente nella form del sito 
        #se coincidano con quelle presenti nel database
        for utente in utenti:
            if utente[1] == nome:
                session["nomeutente"] = nome
                erroreN = True
                if utente[2] == cognome:
                    session["cognomeutente"] = cognome
                    erroreC = True
                    if utente[3] == email:
                        session["emailutente"] = email
                        erroreE = True
                        if utente[4] == password:
                            session["idUtente"] = utente[0]
                            erroreP = True
        #errore di accesso
        if erroreN == True:
            if erroreC == True:
                if erroreE == True:
                    if erroreP == True:
                        #accesso corretto --> nuova pagina home
                        return redirect(url_for("home"))
                    else:
                        flash("ERRORE, password utente errato","danger")
                else:
                    flash("ERRORE, email utente errato","danger")
            else:
                flash("ERRORE, cognome utente errato","danger")
        else:
            flash("ERRORE, nome utente errato","danger")
                   
    return render_template('login.html')

#funzione pagina di home
@app.route('/home', methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        return redirect(url_for("prenotazione"))
    return render_template("home.html")

#funzione pagina di prenotazione
@app.route('/prenotazione', methods=['GET', 'POST'])
def prenotazione():
    if request.method == "POST":
        #salvataggio i dati inviati dalla form
        session["orario"] = request.form["sel1"]
        session["palestra"] = request.form["optradio"]
        session["dataPrenotata"] = request.form["calendario"]
        print(session["dataPrenotata"])
        #select dell'id_azienda corrispondente al nome dell'azienda
        cursor = conn.cursor()
        query = "SELECT ID_AZIENDA FROM BUON_AZIENDA WHERE NOME=%s"
        cursor.execute(query, (session["palestra"]))
        id_azienda = cursor.fetchone()[0]
        session["idAzienda"] = id_azienda
        print(session["idAzienda"])
        print(session["orario"])
        #controllo che l'utente sia un cliente dell'azienda selezionata
        query = "SELECT ID_UTENTE FROM BUON_ISCRIZIONE_AZIENDA WHERE ID_AZIENDA=%s"
        cursor.execute(query, (session["idAzienda"]))
        id_utente = cursor.fetchall()
        print(id_utente)    
        for id_utente in id_utente:
            if session["idUtente"] == id_utente[0]:
                #palestra selezionata corretta --> passaggio alla nouva funzione per selezionare la sede 
                return redirect(url_for("sede"))
            else:
                #errore nella selezione della palestra
                flash("ERRORE, non sei un cliente della palestra selezionata, riprovare","danger")
                break
    return render_template('prenotazione.html')

#funzione pagina sede
@app.route('/sede', methods=['GET', 'POST'])
def sede():
    sedi={"McFit" : ["Viale Fulvio Testi, 29, 20126", "Via Pier Francesco Mola, Via Ludovico di Breme, 46, 20156", "Via Luisa Battistotti Sassi, 11/B, 20133"], 
    "VirginActive" : ["Via Carlo Imbonati, 24, 20159", "Corso Como, 15, 20154", "Viale Sarca, 232, 20126", "Via del Vecchio Politecnico, 4, 20121"],
    "GetFit" : ["Viale Stelvio, 65, 20159", "Via Giovanni Cagliero, 14, 20125", "Via Cenisio, 10, 20154"],
    "YouFit" : ["Via Ippolito Rosellini, 14, 20124", "Viale Abruzzi, 38, 20131", "Via Privata Giovanni Livraghi, 1, 20126"],
    "FitActive" : ["Viale Stelvio, 47, 20159", "Via Pellegrino Rossi, 88, 20161", "Via Gustavo Modena, 10, 20129", "Via Isaac Newton nº8, 20016"]}
    if request.method == "POST":
        #id utente
        session["idUtente"]
        #salvataggio in sessione dell'indirizzo selezionato nella form
        indirizzoSede =  request.form["optradio"]
        print(indirizzoSede)
        #select per ricavare l'id palestra del corrispettivo indirizzo della sede
        cursor = conn.cursor()
        query = "SELECT ID_PALESTRA FROM BUON_PALESTRA WHERE INDIRIZZO=%s"
        cursor.execute(query, (indirizzoSede))
        #id palestra
        idPalestra = cursor.fetchone()[0]
        print(idPalestra)
        #data prenotazione
        data = datetime.now()
        print(data)
        #data prenotata
        session["dataPrenotata"]
        #orario di inizio e orario di fine
        orarioInizioFine = session["orario"].split(' - ')
        print(session["orario"])
        print(orarioInizioFine[0] +" "+ orarioInizioFine[1])
        #inserimento nel db della prenotazione
        query = "INSERT INTO BUON_PRENOTAZIONE VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query, (orarioInizioFine[0], orarioInizioFine[1], data, session["dataPrenotata"], str(session["idUtente"]), str(idPalestra)))
        #passaggio alla nuova funzione per confermare l'esito
        return redirect(url_for("esito"))

    print(sedi[session["palestra"]])
    #passaggio alla pagina html di palestra e sedi per permettere che siano mostrate in essa
    return render_template('sede.html', palestra=session["palestra"], sedi=sedi[session["palestra"]])

#funzione pagina esito
@app.route('/esito', methods=['GET', 'POST'])
def esito():
    #esecuzione del metodo post
    if request.method == "POST":
        return render_template('home.html')
    #richiedere dati al db per confermare l'esito
    cursor = conn.cursor()
    query = "SELECT TOP 1 * FROM BUON_PRENOTAZIONE ORDER BY ID_PRENOTAZIONE"
    cursor.execute(query)
    esito = cursor.fetchone()
    print(esito)
    #select per ricavare l'indirizzo e l'id azienda della corrispettivo id palestra
    query = "SELECT INDIRIZZO, ID_AZIENDA FROM BUON_PALESTRA WHERE ID_PALESTRA=%s"
    cursor.execute(query, (esito[6]))
    risultato = cursor.fetchone()
    print(risultato)
    #select per ricavare il nome dell'azienda in base al corrispettivo id azienda
    query = "SELECT NOME FROM BUON_AZIENDA WHERE ID_AZIENDA=%s"
    cursor.execute(query, (risultato[1]))
    nomeAzienda = cursor.fetchone()[0]
    #return della pagina html esito passando a essa l'esito, nome azienda e l'indirizzo ricavati in precedenza
    return render_template('esito.html', esito=esito , nomeAzienda=nomeAzienda, indirizzo=risultato[0])

if __name__=="__main__":
    app.run(debug=True)