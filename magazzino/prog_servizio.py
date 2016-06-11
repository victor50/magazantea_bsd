#-*- coding: utf-8 -*-


def EseguiQuery(query):
    """
        Esegue una generica query (formato testo del.")
        restituisce la lista dei risultati
        Esempio Ris=EseguiQuery("SELECT * FROM miatabella")
    """
    from django.db import connection
    cursor=None
    cursor= connection.cursor()
    cursor.execute(query, [])
    return cursor.fetchall()


def Giacenze():
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

