from  magazzino.models import ArticoliLista,PazientiStorico,MovimentoOperazione, Movimentomag, MovimentoOrdine,MovimentoOrdineDettaglio

data=datetime.now().strftime('%d-%m-%Y ore %H:%M')
# Estrai tutti i fornitori
z=PazientiStorico.objects.filter(cessato=True).order_by('cognome','nome')
d = {}
for zz in z:
    y=MovimentoOperazione.objects.filter(paziente=zz)
    lista=[]
    for yy in y:
        w=Movimentomag.objects.filter(tipomov=yy.pk)
        for ww in w:
            p=ArticoliLista.objects.filter(codice=ww.codarticolo_id,restituzione=1)
# Estrai gli articoli da ordinare di ciascun fornitore individuato dal nome
# Se p non è nullo inserisci la voce nel dizionario d dove la chiave è il nome del fornitore
            if p:
                L = [(t.codice,t.descrizione) for t in p]
                lista.append(L[0])
    y=MovimentoOrdine.objects.filter(paziente=zz)
    for yy in y:
        w=MovimentoOrdineDettaglio.objects.filter(id_ordine=yy.pk)
        for ww in w:
            p=ArticoliLista.objects.filter(codice=ww.codarticolo_id,restituzione=1)
            if p:
                L = [(t.codice,t.descrizione) for t in p]
                lista.append(L[0])
    lista
    d[zz.cognome + ', ' +zz.nome]=lista


from  magazzino.models import Articoli,Fornitori
from django.db.models import F
#p=Articoli.objects.filter(giacenza__lte=F('scortaminima'), scortaminima__gt=0).order_by('giacenza','scortaminima')
#for q in p:
#    print("%s %s Giacenza %s   Scorta Minima  %s Forn. %s") % (q.codice, q.descrizione,q.giacenza,q.scortaminima,q.fornitore.all())
#
#Articoli.objects.filter(fornitore__nome__startswith='SISTAGENIX WOUND MANAGEMENT')

z=Fornitori.objects.all().order_by('nome')
d = {}
for zz in z:
    p=Articoli.objects.filter(fornitore__nome=zz.nome,giacenza__lte=F('scortaminima'), scortaminima__gt=0)
    if p:
        ppp = []
        ppp=[[t.codice,t.descrizione,t.giacenza,t.scortaminima] for t in p]
        d[zz.nome] = ppp


data = {'a': [ [1, 2] ], 'b': [ [3, 4] ],'c':[ [5,6]] }

You can use the dict.items() method to get the dictionary elements:

<table>
    <tr>
        <td>a</td>
        <td>b</td>
        <td>c</td>
    </tr>

    {% for key, values in data.items %}
    <tr>
        <td>{{key}}</td>
        {% for v in values[0] %}
        <td>{{v}}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
from magazzino.models import Articoli
conta = Articoli.objects.count()

N=conta/9
R=conta % 9
F={}

for j in range(N):
    F[j] = [i+j*9 for i in range(9)]

if R>0:
    F[j+1] = [i+(j+1)*9 for i in range(R)]

q = Articoli.objects.all()
if R>0:
    for j in range(N+1):
        [(q[i].codice,q[i].descrizione) for i in F[j]]
else:
    for j in range(N):
        [(q[i].codice,q[i].descrizione) for i in F[j]]

if R>0:
    Risultato = []
    appoggio = []
    for j in range(N+1):
        appoggio = [(q[i].codice,q[i].descrizione,q[i].codice_a_barre.name) for i in F[j]]
        Risultato.append(appoggio)
        appoggio = []
else:
    for j in range(N):
        [(q[i].codice,q[i].descrizione) for i in F[j]]


if R>0:
    Risultato = []
    appoggio = []
    for j in range(N+1):
        appoggio = [(q[i]) for i in F[j]]
        Risultato.append(appoggio)
        appoggio = []

from magazzino.barcode import CreaCodiceBarra
from magazzino.models import Articoli
from magazantea.settings import MEDIA_ROOT
q=Articoli.objects.all()
for a in q:
    cod= a.codice.replace(" ", "_").replace("/","_")
    nomefile= MEDIA_ROOT + str(cod)+ '.png'
    CreaCodiceBarra(a.codice)
    a.codice_a_barre=str(cod)+ '.png'
    q.filter(codice=a.codice).update(codice_a_barre=str(cod)+ '.png')

    q.filter(codice=a.codice).update(codice_a_barre=str(cod)+ '.png')


down vote
accepted
Add a CSS class called "pagebreak" (or "pb"), like so:

.pagebreak { page-break-before: always; } // page-break-after works, as well
Then add an empty DIV, SPAN, or P tag where you want the page break.

<span class="pagebreak" />
It won't show up on the page, but will break up the page when printing.

q=Articoli.objects.all()
l=len(q)/9.0

##############################


from magazzino.models import Articoli
from magazantea.settings import MEDIA_ROOT
q=Articoli.objects.all()
for a in q:
    cod= a.codice.lstrip().rstrip().replace(" ", "_").replace("/","_")
    nomefile= MEDIA_ROOT + str(cod)+ '.png'
    CreaCodiceBarra(a.codice,nomefile)
    Articoli.objects.filter(codice=a.codice).update(codice_a_barre=str(cod)+ '.png')




def export_Articoli_da_ordinare_xls(modeladmin, request, queryset):
    """
    Generic xls export admin action.
    """
    from magazzino.signals import EseguiQuery
    from magazzino.models import Movimentomag, MovimentoFatturaDettaglio, Articoli

#   Deve essere un utente di staff a richiedere le info
    if not request.user.is_staff:
        raise PermissionDenied
    opts = modeladmin.model._meta
#
# Determinazione degli articoli la cui giacenza è inferiore al livello di scorta minima
#
    ArticoliinGiacenza = """SELECT p.codarticolo_id as codice,SUM(p.totalepezzi * s.segno) as totale
        FROM movimentomag p INNER JOIN movimentooperazione s
        WHERE p.tipomov_id = s.id
        GROUP BY p.codarticolo_id
        ORDER BY p.codarticolo_id"""
    #Articoli entrati con bolla o fattura
    ArticoliinEntrataFB = """SELECT codarticolo_id as codice,SUM(totalepezzi) as totale
        FROM movimentofatturadettaglio
        GROUP BY codarticolo_id
        ORDER BY codarticolo_id"""
    #
    #AG Rappresenta il SALDO degli articoli in giacenza
    #FB Rappresenta la giacenza degli articoli in entrata con bolla/fattura
    AG= EseguiQuery(ArticoliinGiacenza)
    FB= EseguiQuery(ArticoliinEntrataFB)
    REC={}
    if AG and FB:
        for a in AG:
            REC[a[0]] = a[1]
        for b in FB:
            if b[0] in REC.keys():
                REC[b[0]] += b[1]
            else:
                REC[b[0]] = b[1]
#
    elif not AG and FB:
        for b in FB:
            REC[b[0]] = b[1]
#
    elif AG and not FB:
        for a in AG:
            REC[a[0]] = a[1]
#
    #Sostituisce il valore di giacenza per gli articoli in entrata/uscita senza fattura
    [Articoli.objects.filter(pk=t).update(giacenza=int(REC[t])) for t in REC]
 #
    f= (lambda x,y: x if x<= y else None)
    d = [(t,f(Articoli.objects.get(pk=t).giacenza,Articoli.objects.get(pk=t).scortaminima)) for t in REC.keys()]
    wb = Workbook()
    ws0 = wb.add_sheet('0')
    col = 0
    field_names = ['descrizione','codice', 'data_di_inserimento', 'data_di_modifica', 'categoria', 'Codice_IVA', 'prezzo', 'sconto', 'prezzo_scontato', 'giacenza']

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
export_Articoli_da_ordinare_xls.short_description = "Lista Articoli da ordinare in Excel"








from magazzino.signals import EseguiQuery
from magazzino.models import Movimentomag,MovimentoFatturaDettaglio,Articoli
mm=Movimentomag.objects.filter(totalepezzi__gt=0).order_by("codarticolo")
mf=MovimentoFatturaDettaglio.objects.filter(totalepezzi__gt=0).order_by("codarticolo")
for p in mm:
    print(p.codarticolo,p.totalepezzi)

for q in mf:
    print(q.codarticolo,q.totalepezzi)

from django.db.models import Sum, Count

mm.aggregate(num=Count('codarticolo'),Totale=Sum('totalepezzi'))

MovimentiSenzaFattura = """
            SELECT p.codarticolo_id as codice, z.descrizione, SUM(p.totalepezzi * s.segno) as totale
            FROM movimentomag p, Articoli z INNER JOIN movimentooperazione s
            WHERE p.tipomov_id = s.id  and z.codice= p.codarticolo_id
            GROUP BY p.codarticolo_id
            ORDER BY p.codarticolo_id"""

EseguiQuery(MovimentiSenzaFattura)

MovimentiConFattura = """
            SELECT p.codarticolo_id as codice, z.descrizione, SUM(p.totalepezzi) as totale
            FROM movimentofatturadettaglio p, Articoli z INNER JOIN movimentofattura s
            WHERE p.tipomov_id = s.id  and z.codice= p.codarticolo_id
            GROUP BY p.codarticolo_id
            ORDER BY p.codarticolo_id"""

EseguiQuery(MovimentiConFattura)

ScorteCarenti = """
            SELECT codice, descrizione, giacenza,scortaminima FROM articoli
            WHERE giacenza <= scortaminima and scortaminima >0
            ORDER BY descrizione"""

EseguiQuery(ScorteCarenti)





from magazzino.models import Articoli,MovimentoFatturaDettaglio,Movimentomag
from datetime import datetime
#Se c'è almeno un record in MovimentoFatturaDettaglio.objects e\o in Movimentomag
# calcola giacenze
if (MovimentoFatturaDettaglio.objects.all().count() + Movimentomag.objects.all().count()):
#Articoli imputati in entrata o uscita senza bolla o fattura
#s.segno può dunque valere 1 o -1
    ArticoliinGiacenza = """SELECT p.codarticolo_id as codice,SUM(p.totalepezzi * s.segno) as totale
        FROM movimentomag p INNER JOIN movimentooperazione s
        WHERE p.tipomov_id = s.id
        GROUP BY p.codarticolo_id
        ORDER BY p.codarticolo_id"""
    #Articoli entrati con bolla o fattura
    ArticoliinEntrataFB = """SELECT codarticolo_id as codice,SUM(totalepezzi) as totale
        FROM movimentofatturadettaglio
        GROUP BY codarticolo_id
        ORDER BY codarticolo_id"""
    #AG Rappresenta il SALDO degli articoli in giacenza
    #FB Rappresenta la giacenza degli articoli in entrata con bolla/fattura
    AG= EseguiQuery(ArticoliinGiacenza)
    FB= EseguiQuery(ArticoliinEntrataFB)
    REC={}
    if AG and FB:
        for a in AG:
            REC[a[0]] = a[1]
        for b in FB:
            if b[0] in REC.keys():
                REC[b[0]] += b[1]
            else:
                REC[b[0]] = b[1]
#
    elif not AG and FB:
        for b in FB:
            REC[b[0]] = b[1]
#
    elif AG and not FB:
        for a in AG:
            REC[a[0]] = a[1]
#
    #Sostituisce il valore di giacenza per gli articoli in entrata/uscita senza fattura    [Articoli.objects.filter(pk=t).update(giacenza=int(REC[t])) for t in REC]
    #Sostituisce il valore di giacenza per gli articoli in entrata/uscita senza fattura
    [Articoli.objects.filter(pk=t).update(giacenza=int(REC[t])) for t in REC]
 #
    f= (lambda x,y: x if x<= y else None)
    d=[]
    data=datetime.now()
    data=data.strftime("%d/%m/%y %H:%M")
    for t in REC.keys():
        if (Articoli.objects.get(pk=t).giacenza <= Articoli.objects.get(pk=t).scortaminima):
            d.append((data,t, from magazzino.models import Articoli,MovimentoFatturaDettaglio,Movimentomag
from datetime import datetime
#Se c'è almeno un record in MovimentoFatturaDettaglio.objects e\o in Movimentomag
# calcola giacenze
if (MovimentoFatturaDettaglio.objects.all().count() + Movimentomag.objects.all().count()):
#Articoli imputati in entrata o uscita senza bolla o fattura
#s.segno può dunque valere 1 o -1
    ArticoliinGiacenza = """SELECT p.codarticolo_id as codice,SUM(p.totalepezzi * s.segno) as totale
        FROM movimentomag p INNER JOIN movimentooperazione s
        WHERE p.tipomov_id = s.id
        GROUP BY p.codarticolo_id
        ORDER BY p.codarticolo_id"""
    #Articoli entrati con bolla o fattura
    ArticoliinEntrataFB = """SELECT codarticolo_id as codice,SUM(totalepezzi) as totale
        FROM movimentofatturadettaglio
        GROUP BY codarticolo_id
        ORDER BY codarticolo_id"""
    #AG Rappresenta il SALDO degli articoli in giacenza
    #FB Rappresenta la giacenza degli articoli in entrata con bolla/fattura
    AG= EseguiQuery(ArticoliinGiacenza)
    FB= EseguiQuery(ArticoliinEntrataFB)
    REC={}
    if AG and FB:
        for a in AG:
            REC[a[0]] = a[1]
        for b in FB:
            if b[0] in REC.keys():
                REC[b[0]] += b[1]
            else:
                REC[b[0]] = b[1]
#
    elif not AG and FB:
        for b in FB:
            REC[b[0]] = b[1]
#
    elif AG and not FB:
        for a in AG:
            REC[a[0]] = a[1]
#
    #Sostituisce il valore di giacenza per gli articoli in entrata/uscita senza fattura    [Articoli.objects.filter(pk=t).update(giacenza=int(REC[t])) for t in REC]
    #Sostituisce il valore di giacenza per gli articoli in entrata/uscita senza fattura
    [Articoli.objects.filter(pk=t).update(giacenza=int(REC[t])) for t in REC]
 #
    f= (lambda x,y: x if x<= y else None)
    d=[]
    data=datetime.now()
    data=data.strftime("%d/%m/%y %H:%M")
    for t in REC.keys():
        if (Articoli.objects.get(pk=t).giacenza <= Articoli.objects.get(pk=t).scortaminima):
            d.append((data,t, Articoli.objects.get(pk=t).descrizione, Articoli.objects.get(pk=t).giacenza,Articoli.objects.get(pk=t).scortaminima))
    #
else:
#Se non ci sono record in MovimentoFatturaDettaglio **AND** in Movimentomag
# azzera giacenze di tutti i record di articoli

    Articoli.objects.all().update(giacenza = 0)
    print('Ho azzerato tutte le giacenze')
    return

