#-*- coding: utf-8 -*-

from django.http import HttpResponse
from datetime import datetime
from time import strftime, localtime
from django.core.exceptions import PermissionDenied
from models import Articoli,MovimentoOperazione,Movimentomag,MovimentoFattura,MovimentoFatturaDettaglio,MovimentoOrdine, MovimentoOrdineDettaglio
from re import compile,sub
from StringIO import StringIO
from pyExcelerator import *
from django.db.models import Avg,Sum,Count
from sqlite3 import *

from comune.prog_servizio import EseguiQuery

def export_Articoli_as_xls(modeladmin, request, queryset):
    """
    Generic xls export admin action.
    """
    queryset=Articoli.objects.all()
    #print(queryset.count())
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta

    wb = Workbook()
    ws0 = wb.add_sheet('0')
    col = 0
    field_names = ['descrizione','codice', 'data_di_inserimento', 'data_di_modifica', 'categoria', 'codice_iva', 'prezzo', 'sconto', 'prezzo_scontato', 'giacenza']

    # write header row
    for field in field_names:
        ws0.write(0, col, field)
        #field_names.append(field)
        col = col + 1

    #start=datetime.now()
    row = 1
    # Write data rows
    for obj in queryset:
        col = 0
        for field in field_names:
            val = unicode(getattr(obj, field)).strip()
            if field in ['prezzo', 'sconto', 'prezzo_scontato']:
                p=compile('\.')
                val=p.sub(',',val)
            ws0.write(row, col, val)
            col = col + 1
        row = row + 1

    #end = datetime.now()
    #print(end-start)
    f = StringIO()
    wb.save(f)
    f.seek(0)
    response = HttpResponse(f.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s.xls' % unicode(opts).replace('.', '_')
    f.close()
    return response
export_Articoli_as_xls.short_description = "Esporta Articoli in Excel"


def Partitario_as_xls(modeladmin, request, queryset):
    """
    Partitario dei prodotti selezionati.
    """
    """
    MovimentiArticoliSelezionati=Movimentomag.objects.filter(codarticolo=q).order_by('tipomov__data_movimento')
    for d in MovimentiArticoliSelezionati:
        stringa = "%s %s %s %s %s %s" %(str(d.tipomov.data_movimento)[:16],d.tipomov.paziente.cognome,str(d.tipomov.segno),str(d.numconfezioni),str(d.numerounita),str(d.totalepezzi))
        print stringa
    """
    wb = Workbook()
    ws0 = wb.add_sheet('0')
    riga = 0
    for q in queryset:
        if not request.user.is_staff:
            raise PermissionDenied
        NEntrata = NUscita = NScadenza = 0
        Saldo1 = Saldo2 = Saldo3 = 0
        col = 0
        ws0.write(riga, col, q.codice)
        col = 1
        ws0.write(riga,col,q.descrizione)
        riga += 2
        Saldo1 = 0
#
#
# Entrata/Uscita senza Bolla o Fattura
        MovimentiArticoliSelezionati=Movimentomag.objects.filter(codarticolo=q).order_by('tipomov__data_movimento')
        if MovimentiArticoliSelezionati:
            IntestazioneColonne = ['Data Movimento','Causale', 'Num.Confezioni', 'Num.Pezzi', 'Tot.Pezzi Entrata', 'Tot.Pezzi Uscita','Eliminati x scadenza']
            col = 0
            # write header row
            for field in IntestazioneColonne:
                ws0.write(riga, col, field)
                col = col + 1
            NEntrata = NUscita = NScadenza = 0
            riga += 1
            for d in MovimentiArticoliSelezionati:
                col = 0
                ws0.write(riga, col, str(d.tipomov.data_movimento)[:16])
                col = 1
                ws0.write(riga, col, str(d.tipomov.paziente.cognome))
                col = 2
                ws0.write(riga, col, d.numconfezioni)
                col = 3
                ws0.write(riga, col, d.numerounita)
                if d.tipomov.segno > 0:
                    col = 4
                    ws0.write(riga, col, d.totalepezzi)
                    NEntrata += d.totalepezzi
                    Saldo1 += d.totalepezzi
                else:
                    if d.tipomov.segno == -1:
                        col = 5
                        ws0.write(riga, col, d.totalepezzi)
                        NUscita += d.totalepezzi
                        Saldo1 -= d.totalepezzi
                    if d.tipomov.segno == -2:
                        col = 6
                        ws0.write(riga, col, d.totalepezzi)
                        NScadenza += d.totalepezzi
                        Saldo1 -= d.totalepezzi
                riga +=1
            riga +=1
            col = 4
            ws0.write(riga, col, NEntrata)
            col = 5
            ws0.write(riga, col, NUscita)
            col = 6
            ws0.write(riga, col, NScadenza)
            riga += 1
            ws0.write(riga, col-1, "SALDO")
            ws0.write(riga, col, Saldo1)
	    riga += 2
#
#
# Movimenti articoli in entrata con bolla o fattura
        MovimentiArticoliSelezionati = MovimentoFatturaDettaglio.objects.filter(codarticolo=q).order_by('tipomov__data_di_inserimento')
        if MovimentiArticoliSelezionati:
            doctipo={1:'BOLLA',2:'FATTURA', 3:'LISTA SINTESI'}
            IntestazioneColonne = ['Data Movimento','Fornitore','Documento','Data Emissione', 'Num.Confezioni', 'Num.Pezzi', 'Tot.Pezzi Entrata', 'Tot.Pezzi Uscita']
            col = 0
            Saldo2 = 0
            # write header row
            for field in IntestazioneColonne:
                ws0.write(riga, col, field)
                col = col + 1
            riga += 1
            NEntrata = NUscita = 0
            riga += 1
            for d in MovimentiArticoliSelezionati:
                col = 0
                ws0.write(riga, col, str(d.tipomov.data_di_inserimento)[:16])
                col = 1
                ws0.write(riga, col, d.tipomov.fornitore.nome)
                col = 2
                ws0.write(riga, col, doctipo[d.tipomov.documento])
                col = 3
                ws0.write(riga, col, str(d.tipomov.data_documento))
                col = 4
                ws0.write(riga, col, d.numconfezioni)
                col = 5
                ws0.write(riga, col, d.numerounita)
                col = 6
                ws0.write(riga, col, d.totalepezzi)
                NEntrata += d.totalepezzi
                Saldo2 += d.totalepezzi
                riga +=1
            riga +=1
            col = 6
            ws0.write(riga, col, NEntrata)
            riga += 1
            ws0.write(riga, col-1, "SALDO")
            ws0.write(riga, col, Saldo2)
            riga += 1
#
# MovimentoOrdineDettaglio(id, id_ordine_id, codarticolo_id, numconfezioni, numerounita, totalepezzi, fatto)
# Movimenti articoli in uscita con ordine da Oracle
        MovimentiArticoliSelezionati = MovimentoOrdineDettaglio.objects.filter(codarticolo=q, fatto=True).order_by('id_ordine_id')
        if MovimentiArticoliSelezionati:
            doctipo={1:'BOLLA',2:'FATTURA', 3:'LISTA SINTESI'}
            IntestazioneColonne = ['Data Emissione','Ordine','Paziente', 'Num.Confezioni', 'Num.Pezzi', 'Tot.Pezzi Uscita']
            col = 0
            Saldo3 = 0
            # write header row
            for field in IntestazioneColonne:
                ws0.write(riga, col, field)
                col = col + 1
            riga += 1
            NUscita = 0
            riga += 1
            for d in MovimentiArticoliSelezionati:
                col = 0
                ws0.write(riga, col, str(d.id_ordine.data_emissione))
                col = 1
                ws0.write(riga, col, d.id_ordine_id)
                col = 2
                ws0.write(riga, col, str(d.id_ordine.paziente))
                col = 3
                ws0.write(riga, col, d.numconfezioni)
                col = 4
                ws0.write(riga, col, d.numerounita)
                col = 5
                ws0.write(riga, col, d.totalepezzi)
                NUscita += d.totalepezzi
                Saldo3 += d.totalepezzi
                riga +=1
            riga +=1
            col = 5
            ws0.write(riga, col, NUscita)
            riga += 1
            ws0.write(riga, col-1, "SALDO")
            ws0.write(riga, col, Saldo3)
            riga += 2
            ws0.write(riga, col-1, "GIACENZA")
            ws0.write(riga, col, (Saldo1+Saldo2-Saldo3))
	    riga += 2

    f = StringIO()
    wb.save(f)
    f.seek(0)
    response = HttpResponse(f.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Partitario.xls'
    f.close()
    return response
Partitario_as_xls.short_description = "Partitario Articoli"


def StatisticheArticoli_as_xls(modeladmin, request, queryset):
    # ordinamento per indici di lista
    def rank_simple(vector):
        return sorted(range(len(vector)), key=vector.__getitem__)

    categorie_abbreviazioni = ((1, 'Farmaci','FA'), (2, 'Dispositivi sanitari','DS'),\
         (3, 'Generale','GE'),  (4, 'Materiale di consumo','MC'), (5, 'Medicazioni','ME'),)

    categoria = [(cat[0],cat[1]) for cat in categorie_abbreviazioni]

    wb = Workbook()
    ws0 = wb.add_sheet('0')
    riga = 0
    col = 0
    ws0.write(riga,col,'STATISTICHE COSTI ARTICOLI FORNITI AI PAZIENTI DAL 2015-01-01 00:00 AL'+str(datetime.now())[:16])
    riga +=2
    # intestazione tabella excel
    field_names = ['Articolo','Codice', 'Totale unità', 'Costo unitario', 'Totale costo']
    col = 0

    #Loop per categoria
    for cat in categoria:
        ws0.write(riga,0,'Categoria: '+cat[1])
        riga +=2
        # Scrivi intestazioni di riga
        col = 0
        for field in field_names:
            ws0.write(riga, col, field)
            col = col + 1
        riga +1
        #Estrai da Movimentomag e somma per articolo di quella specifica categoria
        a=Movimentomag.objects.filter(tipomov__segno=-1,tipomov__data_di_inserimento__year=2015,codarticolo__categoria=cat[0]).values('codarticolo__descrizione','codarticolo_id').annotate(totale=Sum('totalepezzi'),costo=Avg('codarticolo__prezzo_scontato')).order_by('codarticolo__descrizione')
        dati=[]
        totale_costo = 0
        #crea lista dati contenente descrizione articolo, codice, numero articoli forniti,
        #prezzo unitario, costo totale ciascun articolo fornito
        for x in a:
            dati.append((x['codarticolo__descrizione'],x['codarticolo_id'],x['totale'],x['costo'],round(x['totale']*x['costo'],2)))
        #   print(x['codarticolo__descrizione'],x['codarticolo_id'],str(x['totale']),str(x['costo']),str(round(x['totale']*x['costo'],2)))
            totale_costo += round(x['totale']*x['costo'],2)
        # Crea in mat lista dei costi totali
        mat=[y[4] for y in dati]
        # Determina indici di lista mat in ordine crescente
        ord=rank_simple(mat)
        # e in ordine decrescente
        ord.reverse()
        # Ordina lista dati in ordine decrescente di costo totale
        querys=[dati[x] for x in ord]
        # Scrivi righe di dati excel
        for x in querys:
            ws0.write(riga,0,x[0])
            ws0.write(riga,1,x[1])
            ws0.write(riga,2,x[2])
            ws0.write(riga,3,x[3])
            ws0.write(riga,4,x[4])
            riga +=1
    #        print(x[0],x[1],str(x[2]),str(x[3]), str(x[4]))
        riga +=1
        ws0.write(riga,4,totale_costo)
        riga +=2
    f = StringIO()
    wb.save(f)
    f.seek(0)
    response = HttpResponse(f.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=StatisticheArticoliUscita.xls'
    f.close()
    return response
StatisticheArticoli_as_xls.short_description = "Statistiche Articoli in uscita"

def Articoli_Pazienti_xls(modeladmin, request, queryset):
    """
    Sommario degli articoli (in ordine alfabetico) complessivi prelevati
    dai singoli pazienti (in ordine alfabetico) .
    """

    """
    Mette in "lista" tutti gli id dei pazienti selezionati
    e li trasforma in tuple (id1, id2, etc...) ed in stringa
    per poter utilizzare la lista nella query
    Inoltre, elimina dalla tuple l'eventuale fine in ",)" (es. '(17534,)')
    """

    lista = []
    for q in queryset:
        lista.append(q.pk)
    lista = str(tuple(lista))
    lista.replace(",)",")")

# Attiva un db sqlite3 in memoria
    conn=connect(':memory:')
    c=conn.cursor()
    c.execute('CREATE TABLE "dato" ("cognome" text NOT NULL,"nome" text NOT NULL,"id" integer NOT NULL,"descrizione" text NOT NULL,"quant" integer NOT NULL);')

    query1= """
        SELECT a.cognome,
            a.nome,
            a.id,
            c.descrizione,
            sum(b.totalepezzi) AS totale_pezzi
           FROM uscita_da_magazzino a,
            movimentomag b,
            articoli c
          WHERE (("""
    query2 = "a.id in "+ lista + ")"
    query3 = """
          AND (a.id_op = b.tipomov_id) AND ((b.codarticolo_id)::text = (c.codice)::text))
          GROUP BY a.cognome, a.nome, a.id, c.descrizione
          ORDER BY a.cognome, a.nome, a.id, c.descrizione
          """

    query = query1 + query2 + query3

    ris = EseguiQuery(query)
    if ris:
        c.executemany('INSERT INTO dato VALUES (?,?,?,?,?)', ris)

    query1= """
        SELECT a.cognome,
            a.nome,
            a.id,
            c.descrizione,
            sum(b.totalepezzi) AS totale_pezzi
           FROM uscita_da_spider a,
            ordinespiderdettaglio b,
            articoli c
          WHERE (("""
    query2 = "a.id in "+ lista + ")"
    query3 = """
          AND (a.id_op = b.id_ordine) AND ((b.codarticolo_id)::text = (c.codice)::text))
          GROUP BY a.cognome, a.nome, a.id, c.descrizione
          ORDER BY a.cognome, a.nome, a.id, c.descrizione
          """
    query = query1 + query2 + query3

    if ris:
        c.executemany('INSERT INTO dato VALUES (?,?,?,?,?)', ris)

    """
    Estrae tutto  registrato nel db in memoria ordinato per cognome,nome,id,descrizione
    e lo scrive nel foglio excel
    """

    c.execute('SELECT cognome,nome,id,descrizione,sum(quant) FROM dato GROUP BY cognome,nome,id,descrizione ORDER BY cognome,nome,id,descrizione')
    rec1 = c.fetchone()
    resto=c.fetchall()
    wb = Workbook()
    ws0 = wb.add_sheet('0')
    riga = 0
    col = 0
    contatore = 0
    IntestazioneColonne = ['Cognome','Nome','Cod.Paziente','Descrizione Articolo', 'Num.Pezzi']
    for i in IntestazioneColonne:
        ws0.write(riga, col, i)
        col +=1
    riga = 1
    paz = rec1[2]
    col = 0
    ws0.write(riga, col, rec1[0])
    col = 1
    ws0.write(riga,col,rec1[1])
    col = 2
    ws0.write(riga,col,rec1[2])
    col = 3
    ws0.write(riga,col,rec1[3])
    col = 4
    ws0.write(riga,col,rec1[4])
    contatore +=1
    riga +=1
    for q in resto:
        if q[2] <> paz:
            contatore = 0
            paz = q[2]
        if contatore == 0:
            col = 0
            ws0.write(riga, col, q[0])
            col = 1
            ws0.write(riga,col,q[1])
            col = 2
            ws0.write(riga,col,q[2])
            col = 3
            ws0.write(riga,col,q[3])
            col = 4
            ws0.write(riga,col,q[4])
            contatore +=1
            riga +=1
        else:
            col = 3
            ws0.write(riga,col,q[3])
            col = 4
            ws0.write(riga,col,q[4])
            contatore +=1
            riga +=1
    f = StringIO()
    wb.save(f)
    f.seek(0)
    response = HttpResponse(f.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=ArticolixPazienti_'+strftime("%Y-%m-%d_%H%M%S", localtime())+'.xls'
    f.close()
    conn.close()
    return response
Articoli_Pazienti_xls.short_description = "Articoli forniti ai pazienti SELEZIONATI"

def Articoli_Pazienti_tutti_xls(modeladmin, request, queryset):
    """
    Sommario degli articoli (in ordine alfabetico) complessivi prelevati
    dai singoli pazienti (in ordine alfabetico) .
    """

    """
    Mette in "queryset" tutti gli id dei pazienti
    """
    from magazzino.models import Pazienti
    queryset = Pazienti.objects.all()
#
# Attiva un db sqlite3 in memoria
#
    conn=connect(':memory:')
    c=conn.cursor()
    c.execute('CREATE TABLE "dato" ("cognome" text NOT NULL,"nome" text NOT NULL,"id" integer NOT NULL,"descrizione" text NOT NULL,"quant" integer NOT NULL);')

    query= """
        SELECT a.cognome,
            a.nome,
            a.id,
            c.descrizione,
            sum(b.totalepezzi) AS totale_pezzi
           FROM uscita_da_magazzino a,
            movimentomag b,
            articoli c
          WHERE ((a.id_op = b.tipomov_id) AND ((b.codarticolo_id)::text = (c.codice)::text))
          GROUP BY a.cognome, a.nome, a.id, c.descrizione
          ORDER BY a.cognome, a.nome, a.id, c.descrizione
          """

    ris = EseguiQuery(query)
    if ris:
        c.executemany('INSERT INTO dato VALUES (?,?,?,?,?)', ris)

    query= """
        SELECT a.cognome,
            a.nome,
            a.id,
            c.descrizione,
            sum(b.totalepezzi) AS totale_pezzi
           FROM uscita_da_spider a,
            ordinespiderdettaglio b,
            articoli c
          WHERE (((a.id_op = b.id_ordine) AND ((b.codarticolo_id)::text = (c.codice)::text))
          GROUP BY a.cognome, a.nome, a.id, c.descrizione
          ORDER BY a.cognome, a.nome, a.id, c.descrizione
          """

    if ris:
        c.executemany('INSERT INTO dato VALUES (?,?,?,?,?)', ris)

    """
    Estrae tutto  registrato nel db in memoria ordinato per cognome,nome,id,descrizione
    e lo scrive nel foglio excel
    """

    c.execute('SELECT cognome,nome,id,descrizione,sum(quant) FROM dato GROUP BY cognome,nome,id,descrizione ORDER BY cognome,nome,id,descrizione')
    rec1 = c.fetchone()
    resto=c.fetchall()
    wb = Workbook()
    ws0 = wb.add_sheet('0')
    riga = 0
    col = 0
    contatore = 0
    IntestazioneColonne = ['Cognome','Nome','Cod.Paziente','Descrizione Articolo', 'Num.Pezzi']
    for i in IntestazioneColonne:
        ws0.write(riga, col, i)
        col +=1
    riga = 1
    paz = rec1[2]
    col = 0
    ws0.write(riga, col, rec1[0])
    col = 1
    ws0.write(riga,col,rec1[1])
    col = 2
    ws0.write(riga,col,rec1[2])
    col = 3
    ws0.write(riga,col,rec1[3])
    col = 4
    ws0.write(riga,col,rec1[4])
    contatore +=1
    riga +=1
    for q in resto:
        if q[2] <> paz:
            contatore = 0
            paz = q[2]
        if contatore == 0:
            col = 0
            ws0.write(riga, col, q[0])
            col = 1
            ws0.write(riga,col,q[1])
            col = 2
            ws0.write(riga,col,q[2])
            col = 3
            ws0.write(riga,col,q[3])
            col = 4
            ws0.write(riga,col,q[4])
            contatore +=1
            riga +=1
        else:
            col = 3
            ws0.write(riga,col,q[3])
            col = 4
            ws0.write(riga,col,q[4])
            contatore +=1
            riga +=1
    f = StringIO()
    wb.save(f)
    f.seek(0)
    response = HttpResponse(f.read(), content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename=ArticolixPazienti_'+strftime("%Y-%m-%d_%H%M%S", localtime())+'.xls'
    f.close()
    conn.close()
    return response
Articoli_Pazienti_tutti_xls.short_description = "Articoli forniti a TUTTI i pazienti"
def Stampa_Rapporto(modeladmin, request, queryset):
    from django.http import HttpResponse
    from magazzino.models import Movimentomag,Articoli
    r = HttpResponse()
    testo ="""<!DOCTYPE html>
        <html lang="it" >
        <head>
        <title>Magazzino ANTEA</title>
        <link rel="stylesheet" type="text/css" href="/static/admin/css/base.css" />
        <link rel="stylesheet" type="text/css" href="/static/admin/css/changelists.css" />
        <script type="text/javascript" src="/magazzino/jsi18n/"></script>
        <script type="text/javascript">window.__admin_media_prefix__ = "/static/admin/";</script>
        <script type="text/javascript" src="/static/admin/js/core.js"></script>
        <script type="text/javascript" src="/static/admin/js/admin/RelatedObjectLookups.js"></script>
        <script type="text/javascript" src="/static/admin/js/jquery.js"></script>
        <script type="text/javascript" src="/static/admin/js/jquery.init.js"></script>
        <script type="text/javascript" src="/static/admin/js/actions.js"></script>
        <script type="text/javascript">
        (function($) {
            $(document).ready(function($) {
                $("tr input.action-select").actions();
            });
        })(django.jQuery);
        </script>
        <meta name="robots" content="NONE,NOARCHIVE" />
        </head>
        <body class="change-list">
        <div id="container">
            <div id="header">
                <div id="branding">
        <h1 id="site-name">Gestione Magazzino - Lista dei movimenti di magazzino senza bolla/fattura</h1>
                </div>
                <div id="user-tools">
                    Benvenuto/a,
                    <strong>victor</strong>.
                            <a href="/magazzino/magazzino/"> / Torna a Magazzino</a> /
                        <a href="/magazzino/password_change/">Cambia la password</a> /
                        <a href="/magazzino/logout/">Annulla l'accesso</a>
            </div>
            </div>
        </body>
        <style>
        .break { page-break-before: always;}
        p.CaratterePiccolo {font-size: 13px;}
        h1 {margin-left:10px;}
        </style>
        <style type="text/css">
        table.bottomBorder { border-collapse:collapse; }
        table.bottomBorder td, table.bottomBorder th { border-bottom:1px dotted black;padding:5px; }
        </style>
        <body bgcolor=white lang=IT style='tab-interval:35.4pt'>
        <div class=WordSection1,  style="margin-left:45px">
        """
    r.write(testo)
    for q in queryset:
        if q.segno <0:
            oper = " **** USCITA ARTICOLI ****  "
        else:
            oper = "**** ENTRATA ARTICOLI ****  "
        testo = '<h3>ID record: %s</h3><h3>%s</h3><h3>Paziente: %s </h3><h3>Operatore: %s</h3>' % (q.id, oper, q.paziente, q.operatore)
        r.write(testo)
        r.write('<p> </p>')
        pp= Movimentomag.objects.filter(tipomov_id=q.id)
        totale=0
        totale_FCIVA = 0
        costo=0
        intestazione = """
            <table class=bottomBorder>
            <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes;page-break-after: always;'>
                  <th valign=top style='width:230pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>Articolo</p>
                  </th>
                  <th valign=top style='width:118pt'>
                    <p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>Codice</p>
                  </th>
                  <th valign=top style='width:70pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>Numero Pezzi</p>
                  </th>
                  <th valign=top style='width:150pt'>
                       <p class=CaratterePiccolo align=center style='margin-top:6.0pt;margin-right:0cm; margin-bottom:
                       0cm;margin-left:0cm;margin-bottom:.0001pt;text-align:center'>Costo (Euro)</p>
                    </th>
                </tr>"""
        r.write(intestazione)
        for p in pp:
            art = Articoli.objects.get(pk=p.codarticolo_id)
            costo = art.prezzo_scontato * p.totalepezzi
            totale +=costo
            if art.codice_iva == 100 : totale_FCIVA +=costo
            testo = """
            <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes;page-break-after: always;'>
                  <td valign=top style='width:230pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>%s</p>
                  </td>
                  <td valign=top style='width:118pt'>
                    <p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>%s</p>
                  </td>
                  <td valign=top style='width:70pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>%s</p>
                  </td>
                  <td valign=top style='width:150pt'>
                       <p class=CaratterePiccolo align=center style='margin-top:6.0pt;margin-right:0cm; margin-bottom:
                       0cm;margin-left:0cm;margin-bottom:.0001pt;text-align:center'>%s</p>
                    </td>
                </tr>""" % (p.codarticolo,p.codarticolo_id,p.totalepezzi,str(costo).replace('.',','))
            r.write(testo)
        testo = """
        <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes;page-break-after: always;'>
              <td valign=top style='width:230pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                0cm;margin-left:0cm;margin-bottom:.0001pt;font-weight:bold'><em>%s</em></p>
              </td>
              <td valign=top style='width:118pt'>
                <p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                0cm;margin-left:0cm;margin-bottom:.0001pt'></p>
              </td>
              <td valign=top style='width:70pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                0cm;margin-left:0cm;margin-bottom:.0001pt'></p>
              </td>
              <td valign=top style='width:150pt'>
                   <p class=CaratterePiccolo align=center style='margin-top:6.0pt;margin-right:0cm; margin-bottom:
                   0cm;margin-left:0cm;margin-bottom:.0001pt;text-align:center;font-weight:bold'><em>%s</em></p>
                </td>
            </tr>"""
        r.write(testo % ('Totale Spesa (Euro)',str(round(totale,2)).replace('.',',')))
        r.write(testo % ('di cui Fuori Campo IVA (Euro)',str(round(totale_FCIVA,2)).replace('.',',')))
        r.write('</table>')
        r.write('<p class="break"> </p>')
    r.write("</div>")
    return r
Stampa_Rapporto.short_description = "Prepara stampa rapporto selezionati"

#######################################

def Stampa_Rapp_Fattura(modeladmin, request, queryset):
    from django.http import HttpResponse
    from magazzino.models import MovimentoFatturaDettaglio,Articoli
    r = HttpResponse()
    testo ="""<!DOCTYPE html>
        <html lang="it" >
        <head>
        <title>Magazzino ANTEA</title>
        <link rel="stylesheet" type="text/css" href="/static/admin/css/base.css" />
        <link rel="stylesheet" type="text/css" href="/static/admin/css/changelists.css" />
        <script type="text/javascript" src="/magazzino/jsi18n/"></script>
        <script type="text/javascript">window.__admin_media_prefix__ = "/static/admin/";</script>
        <script type="text/javascript" src="/static/admin/js/core.js"></script>
        <script type="text/javascript" src="/static/admin/js/admin/RelatedObjectLookups.js"></script>
        <script type="text/javascript" src="/static/admin/js/jquery.js"></script>
        <script type="text/javascript" src="/static/admin/js/jquery.init.js"></script>
        <script type="text/javascript" src="/static/admin/js/actions.js"></script>
        <script type="text/javascript">
        (function($) {
            $(document).ready(function($) {
                $("tr input.action-select").actions();
            });
        })(django.jQuery);
        </script>
        <meta name="robots" content="NONE,NOARCHIVE" />
        </head>
        <body class="change-list">
        <div id="container">
            <div id="header">
                <div id="branding">
        <h1 id="site-name">Gestione Magazzino - Lista dei movimenti di magazzino con bolla/fattura</h1>
                </div>
                <div id="user-tools">
                    Benvenuto/a,
                    <strong>victor</strong>.
                            <a href="/magazzino/magazzino/"> / Torna a Magazzino</a> /
                        <a href="/magazzino/password_change/">Cambia la password</a> /
                        <a href="/magazzino/logout/">Annulla l'accesso</a>
            </div>
            </div>
        </body>
        <style>
        .break { page-break-before: always;}
        p.CaratterePiccolo {font-size: 13px;}
        h1 {margin-left:10px;}
        </style>
        <style type="text/css">
        table.bottomBorder { border-collapse:collapse; }
        table.bottomBorder td, table.bottomBorder th { border-bottom:1px dotted black;padding:5px; }
        </style>
        <body bgcolor=white lang=IT style='tab-interval:35.4pt'>
        <div class=WordSection1,  style="margin-left:45px">
        """
    r.write(testo)
    for q in queryset:
        if q.documento==1:
            tipodoc= 'BOLLA'
        if q.documento==2:
            tipodoc= 'FATTURA'
        if q.documento==3:
            tipodoc= 'LISTA SINTESI'
        testo = '<h3>ID number: %s</h3><h3>Fornitore: %s </h3><h3>Documento: %s  ------------        Num.Doc. %s  ------------      Data di emissione %s</h3>' % (q.id, q.fornitore, tipodoc, q.numdoc,q.data_documento)
        r.write(testo)
        r.write('<p> </p>')
        pp= MovimentoFatturaDettaglio.objects.filter(tipomov_id=q.id)
        totale=0
        totale_FCIVA = 0
        costo=0
        intestazione = """
            <table class=bottomBorder>
            <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes;page-break-after: always;'>
                  <th valign=top style='width:230pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>Articolo</p>
                  </th>
                  <th valign=top style='width:118pt'>
                    <p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>Codice</p>
                  </th>
                  <th valign=top style='width:70pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>Numero Pezzi</p>
                  </th>
                  <th valign=top style='width:150pt'>
                       <p class=CaratterePiccolo align=center style='margin-top:6.0pt;margin-right:0cm; margin-bottom:
                       0cm;margin-left:0cm;margin-bottom:.0001pt;text-align:center'>Costo (Euro)</p>
                    </th>
                </tr>"""
        r.write(intestazione)
        for p in pp:
            art = Articoli.objects.get(pk=p.codarticolo_id)
            costo = art.prezzo_scontato * p.totalepezzi
            totale +=costo
            if art.codice_iva == 100 : totale_FCIVA +=costo
            testo = """
            <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes;page-break-after: always;'>
                  <td valign=top style='width:230pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>%s</p>
                  </td>
                  <td valign=top style='width:118pt'>
                    <p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>%s</p>
                  </td>
                  <td valign=top style='width:70pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                    0cm;margin-left:0cm;margin-bottom:.0001pt'>%s</p>
                  </td>
                  <td valign=top style='width:150pt'>
                       <p class=CaratterePiccolo align=center style='margin-top:6.0pt;margin-right:0cm; margin-bottom:
                       0cm;margin-left:0cm;margin-bottom:.0001pt;text-align:center'>%s</p>
                    </td>
                </tr>""" % (p.codarticolo,p.codarticolo_id,p.totalepezzi,str(costo).replace('.',','))
            r.write(testo)
        testo = """
        <tr style='mso-yfti-irow:0;mso-yfti-firstrow:yes;page-break-after: always;'>
              <td valign=top style='width:230pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                0cm;margin-left:0cm;margin-bottom:.0001pt;font-weight:bold'><em>%s</em></p>
              </td>
              <td valign=top style='width:118pt'>
                <p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                0cm;margin-left:0cm;margin-bottom:.0001pt'></p>
              </td>
              <td valign=top style='width:70pt'><p class=CaratterePiccolo  align=center style='margin-top:6.0pt;margin-right:0cm;margin-bottom:
                0cm;margin-left:0cm;margin-bottom:.0001pt'></p>
              </td>
              <td valign=top style='width:150pt'>
                   <p class=CaratterePiccolo align=center style='margin-top:6.0pt;margin-right:0cm; margin-bottom:
                   0cm;margin-left:0cm;margin-bottom:.0001pt;text-align:center;font-weight:bold'><em>%s</em></p>
                </td>
            </tr>"""
        r.write(testo % ('Totale Spesa (Euro)',str(round(totale,2)).replace('.',',')))
        r.write(testo % ('di cui Fuori Campo IVA (Euro)',str(round(totale_FCIVA,2)).replace('.',',')))
        r.write('</table>')
        r.write('<p class="break"> </p>')
    r.write("</div>")
    return r
Stampa_Rapp_Fattura.short_description = "Prepara stampa rapporto selezionati"

