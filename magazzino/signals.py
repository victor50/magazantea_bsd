#-*- coding: utf-8 -*-
from magazzino.prog_servizio import EseguiQuery

def stampa(sender,**kwargs):
    print('Cancellato Record')
    return


def TotaliGiacenze(sender,**kwargs):
    from django.core.cache import cache
    from magazzino.models import Articoli,MovimentoFatturaDettaglio,Movimentomag,MovimentoOrdineDettaglio
    from spider.models import OrdineSpiderDettaglio
    import time
    start_time = time.clock() # Inizio misura tempo esecuzione della procedura
    #Se c'è almeno un record in MovimentoFatturaDettaglio.objects e\o in Movimentomag e/o in MovimentoOrdineDettaglio
    # calcola giacenze
    if (MovimentoFatturaDettaglio.objects.all().count() + Movimentomag.objects.all().count() + MovimentoOrdineDettaglio.objects.all().count() + OrdineSpiderDettaglio.objects.all().count()):
        #Articoli imputati in entrata o uscita senza bolla o fattura
        #s.segno può dunque valere 1 (in entrata) o
        # -1 (in uscita) o -2 (in uscita per scadenza)
        Contatore = 1
    #Seleziona tutti i codici merceologici in Articoli. Serve per calcolo giacenze
        CodGia = 'SELECT codice,giacenza FROM articoli'
    #Articoli in entrata senza bolla/fattura
        ArticoliinGiacenzaIN = """SELECT p.codarticolo_id as codice,SUM(p.totalepezzi) as totale
            FROM movimentomag p INNER JOIN movimentooperazione s
            ON (p.TipoMov_id = s.id)
            WHERE s.segno > 0
            GROUP BY p.codarticolo_id
            ORDER BY p.codarticolo_id"""
    #Articoli in uscita senza bolla/fattura
        ArticoliinGiacenzaOUT = """SELECT p.codarticolo_id as codice,SUM(p.totalepezzi) as totale
            FROM movimentomag p INNER JOIN movimentooperazione s
            ON (p.TipoMov_id = s.id)
            WHERE s.segno < 0
            GROUP BY p.codarticolo_id
            ORDER BY p.codarticolo_id"""
        #Articoli entrati con bolla o fattura
        ArticoliinEntrataFB = """SELECT codarticolo_id as codice,SUM(totalepezzi) as totale
            FROM movimentofatturadettaglio
            GROUP BY codarticolo_id
            ORDER BY codarticolo_id"""
        # Articoli in ordini da ***VECCHIA *** cartella clinica Galileo (dismessa)
        ArticoliinOrdine = """SELECT codarticolo_id as codice,SUM(totalepezzi) as totale
            FROM movimentoordinedettaglio
            WHERE fatto is TRUE
            GROUP BY codarticolo_id
            ORDER BY codarticolo_id"""
        # Articoli in ordini da ***NUOVA*** cartella clinica SPIDER
        ArticoliinSpider = """SELECT codarticolo_id as codice,SUM(totalepezzi) as totale
            FROM ordinespiderdettaglio
            WHERE fatto is TRUE
            GROUP BY codarticolo_id
            ORDER BY codarticolo_id"""

        #AG_IN, AG_OUT Rappresentano il numero degli articoli in Entrata o Uscita per codice merceo
        #FB Rappresenta la giacenza degli articoli in entrata con bolla/fattura
        #OR Rappresenta la giacenza degli articoli in ordini da vecchia cartella clinica GALILEO
        #SP Rappresenta la giacenza degli articoli in ordini da nuova cartella clinica SPIDER
        #CODICI = elenco dei codici presenti nella tabella articoli
        AG_IN = EseguiQuery(ArticoliinGiacenzaIN)
        AG_OUT = EseguiQuery(ArticoliinGiacenzaOUT)
        FB = EseguiQuery(ArticoliinEntrataFB)
        OR = EseguiQuery(ArticoliinOrdine)
        SP = EseguiQuery(ArticoliinSpider)
        CG= EseguiQuery(CodGia)
        CODICI = []
        CODICI = [t[0] for t in CG]
        [cache.set(str(t[0]), t[1],180) for t in CG]
    #
        giacenze = {}
        # Poni tutte le giacenze nella lista uguali a zero
        for c in CODICI:
            giacenze[c] = 0

        if AG_IN:
        #Aggiunge al valore di giacenza il numero di articoli in entrata senza bolla/fattura
            for t in AG_IN:
                giacenze[t[0]] += t[1]

        if AG_OUT:
        #Sottrae al valore di giacenza il numero di articoli in uscita senza bolla/fattura
            for t in AG_OUT:
                giacenze[t[0]] -= t[1]

        if FB:
        #Sostituisce il valore di giacenza per gli articoli in entrata con fattura/bolla
            for t in FB:
                giacenze[t[0]] += t[1]

        if OR:
        #Sostituisce il valore di giacenza per gli articoli in uscita da Galileo
            for t in OR:
                giacenze[t[0]] -= t[1]
        if SP:
        #Sostituisce il valore di giacenza per gli articoli in uscita da Spider
            for t in SP:
                giacenze[t[0]] -= t[1]

	    Contatore = 0
        for c in CODICI:
        #Essendo state azzerate in precedenza tutte le giacenze nel DB non è necessario
        # fare l'update dei codici a giacenza zero. Si guadagna tempo.
           if giacenze[c] != cache.get(str(c)):
            # Sostituisce le giacenze della tabella articoli con quelle della lista giacenze
                Articoli.objects.filter(pk=c).update(giacenza=giacenze[c])
                Contatore += 1

        print("Ricalcolo giacenze con Giacenze() --- %s secondi ---Volte %s") % (time.clock() - start_time, Contatore)

    else:
    #Se non ci sono record in MovimentoFatturaDettaglio **AND** in Movimentomag **AND** in MovimentoOrdineDettaglio
    # azzera giacenze di tutti i record di articoli
        Articoli.objects.all().update(giacenza = 0)
        print('Ho azzerato tutte le giacenze')
    return


def salva_modello(sender, **kwargs):
    utente = unicode(request.user)
    if change:
        obj.modificato_da = utente
    else:
        obj.creato_da = utente


def elimina_file_img(sender, instance, *args, **kwargs):
    '''
        Elimina il file immagine png da /media quando viene eliminata un record
        dal modello Articoli
    '''
    from magazantea.settings import MEDIA_ROOT
    from os import remove
    instance.codice = instance.codice.strip()
    nomefile = instance.codice.replace(" ", "_").replace("/","_").replace(".","_")
    nomefile = MEDIA_ROOT+(str(nomefile)+ '.png')
    try:
        remove(nomefile)
    except:
        pass
    return


def m2m_ModificaArticoliInICEC(sender, instance, action, reverse, model, pk_set, **kwargs):
    from magazzino.models import Articoli
    import psycopg2
    from decimal import Decimal
    my_dict = {}
    my_dict['data_di_inserimento'] = instance.data_di_inserimento
    my_dict['data_di_modifica'] = instance.data_di_modifica
    my_dict['creato_da'] = instance.creato_da
    my_dict['modificato_da'] = instance.modificato_da
    my_dict['codice'] = instance.codice
    my_dict['descrizione'] = instance.descrizione
    my_dict['codice_articolo_fornitore'] = instance.codice_articolo_fornitore
    my_dict['categoria'] = instance.categoria
    my_dict['codice_iva'] = instance.codice_iva
    my_dict['prezzo'] = instance.prezzo
    my_dict['sconto'] = instance.sconto
    my_dict['prezzo_scontato'] = instance.prezzo_scontato
    my_dict['unita_di_misura'] = instance.unita_di_misura
    my_dict['scortaminima'] = instance.scortaminima
    my_dict['note'] = instance.note
    my_dict['quantita_conf'] = instance.quantita_conf
    my_dict['restituzione'] = instance.restituzione
#Verifica valori nulli e sostituisci
    if not my_dict['data_di_inserimento']:
        my_dict['data_di_inserimento'] = '2013-01-11 12:00'
    if not my_dict['data_di_modifica']:
        my_dict['data_di_modifica'] = '2013-01-11 12:00'
    if not my_dict['creato_da']:
        my_dict['creato_da'] = ''
    if not my_dict['modificato_da']:
        my_dict['modificato_da'] = ''
    if not my_dict['codice_articolo_fornitore']:
        my_dict['codice_articolo_fornitore'] = ''
    if not my_dict['note']:
        my_dict['note'] = ''
    if not my_dict['categoria']:
        my_dict['categoria'] = 3
    if not my_dict['codice_iva']:
        my_dict['codice_iva'] = 22
    if not my_dict['prezzo']:
        my_dict['prezzo'] = 0.0
    if not my_dict['sconto']:
        my_dict['sconto'] = 0
    if not my_dict['prezzo_scontato']:
        my_dict['prezzo_scontato'] = 0.0
    if not my_dict['unita_di_misura']:
        my_dict['unita_di_misura'] = 4
    if not my_dict['scortaminima']:
        my_dict['scortaminima'] = 0
    if not my_dict['quantita_conf']:
        my_dict['quantita_conf'] = 0
    if not my_dict['restituzione']:
        my_dict['restituzione'] = 0
    try:
        conn = psycopg2.connect("dbname='magazicec' user='antea' host='192.168.1.30' password='antea'")
    except:
        try:
            conn = psycopg2.connect("dbname='magazicec' user='antea' host='10.20.0.1' password='antea'")
        except:
            print "Non riesco a connettermi al database"
    cur = conn.cursor()
#Elenca record che dovranno andare in articoli_fornitore
    if action == 'post_add':
        for val in pk_set:
            print instance.codice, instance.descrizione, val
        sql_cerca_in_articoli_ICEC ='select * from articoli where codice = '+"$$"+str(my_dict['codice'])+"$$"
        # Verifica se il codice articolo è già in magazicec
        cur.execute(sql_cerca_in_articoli_ICEC)
        ris = cur.fetchall()
        # Se sì, fai un update di tutte le colonne del record in magazicec previa pulizia anomalie
        if ris:
            cur.execute("UPDATE articoli SET datains = "+"$$"+str(my_dict['data_di_inserimento']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET datamod = "+"$$"+str(my_dict['data_di_modifica']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET creato_da = "+"$$"+str(my_dict['creato_da']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET modificato_da = "+"$$"+str(my_dict['modificato_da']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET descrizione = "+"$$"+str(my_dict['descrizione']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET codiceartfor = "+"$$"+str(my_dict['codice_articolo_fornitore']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET categoria = "+"$$"+str(my_dict['categoria']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET codiceiva = "+"$$"+str(my_dict['codice_iva']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET prezzo = "+"$$"+str(my_dict['prezzo']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET sconto = "+"$$"+str(my_dict['sconto']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET prezzo_scontato = "+"$$"+str(my_dict['prezzo_scontato']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET unita_di_misura_id = "+"$$"+str(my_dict['unita_di_misura']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET scortaminima = "+"$$"+str(my_dict['scortaminima']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET note = "+"$$"+str(my_dict['note']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET quantitaxconf = "+"$$"+str(my_dict['quantita_conf']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            cur.execute("UPDATE articoli SET restituzione = "+"$$"+str(my_dict['restituzione']) +"$$ where codice =" + "$$"+str(my_dict['codice']) + "$$")
            conn.commit()
        else:
            sql = "INSERT INTO articoli (datains, datamod, creato_da, modificato_da, "
            sql += "codice, descrizione, codiceartfor, categoria, codiceiva, "
            sql += "prezzo, sconto, prezzo_scontato, unita_di_misura_id, scortaminima,"
            sql += "note, quantitaxconf, restituzione) VALUES ("
            sql += "'"+str(my_dict['data_di_inserimento'])+"','" + str(my_dict['data_di_modifica']) +"','"+my_dict['creato_da']+ "','"+my_dict['modificato_da']+"','"+my_dict['codice'] + "','"+my_dict['descrizione']+"','"+my_dict['codice_articolo_fornitore']+"',"+ str(my_dict['categoria'])+","+str(my_dict['codice_iva'])+","+str(my_dict['prezzo'])+","+str(my_dict['sconto'])+", "+str(my_dict['prezzo_scontato']) +","+str(my_dict['unita_di_misura'])+","+str(my_dict['scortaminima'])+",'"+my_dict['note']+ "',"+str(my_dict['quantita_conf'])+", "+str(my_dict['restituzione'])+")"
            print sql
            cur.execute(sql)
            conn.commit()
# Sia in caso di update che di aggiornamento
#Elenca record in magazantea che dovranno andare in articoli_fornitore in magazicec
#elimina i corrispondenti vecchi record in articoli_fornitore in magazicec
#ricreali daccapo
        if pk_set:
            cur.execute("DELETE FROM articoli_fornitore WHERE articoli_id="+"$$"+str(my_dict['codice'])+"$$")
            conn.commit()
            for val in pk_set:
                print instance.codice, instance.descrizione, val, " ---DA INSERIRE"
                sql = "INSERT INTO articoli_fornitore (articoli_id, fornitori_id) VALUES ("
                sql += "$$"+my_dict['codice']+"$$,"+str(val)+")"
                cur.execute(sql)
            conn.commit()
# Cancellazione di articoli
    if action == 'pre_remove':
        if pk_set:
            print instance.codice, instance.descrizione, val, " ---DA CANCELLARE"
            cur.execute("DELETE FROM articoli_fornitore WHERE articoli_id="+"$$"+str(my_dict['codice'])+"$$")
            conn.commit()
    return


def Elimina_Movimento(sender, instance, *args, **kwargs):
    '''
        Verifica se il record di MovimentoOperazione è quello in cui si è richiesto il kit
        Se sì va a modificare il record pazienti ponendo nrec_kit=0 e dotato_kit=False
    '''
    if (instance.paziente.nrec_kit == instance.pk):
        print "Azzerato nrec_kit"
        instance.paziente.nrec_kit = 0
        instance.paziente.dotato_kit = False
        instance.paziente.save()
    else:
        print "Nulla"
    return
