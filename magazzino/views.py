#-*- coding: utf-8 -*-
# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from models import *

from django.http import HttpResponse

from datetime import datetime
from django.db.models import F

def hello(request):
    return HttpResponse("Digita http://192.168.5.19:8000/magazzino")


@login_required
@cache_page(60 * 15)
def listbarcode(request):
    from magazzino.models import Articoli, posizione, categorie_abbreviazioni
    data=datetime.now().strftime('%d-%m-%Y ore %H:%M')
    conta = Articoli.objects.count()
    N=conta/9
    R=conta % 9
    F={}
# Funzione per trasformare la posizione dell'articolo in stringa stampabile
    def pos(p):
        return (posizione[p.colarm-1][1] + '-' + posizione[p.piano-1][1] + '-' + posizione[p.altrorif1-1][1] + '-' + posizione[p.altrorif2-1][1])
#    pos = lambda p : (posizione[p.colarm-1][1] + '-' + posizione[p.piano-1][1] + '-' + posizione[p.altrorif1-1][1] + '-' + posizione[p.altrorif2-1][1])
# Funzione per estrarre la posizione (indice) della stringa di abbreviazione
# della categoria dell'articolo da categorie_abbreviazioni
    def cat(z):
        for k in range(len(categorie_abbreviazioni)):
            if (z.categoria == categorie_abbreviazioni[k][0]):
                break
        return k
    #
    if (N > 0):
        for j in range(N):
            F[j] = [i+j*9 for i in range(9)]
        if (R>0):
            F[j+1] = [i+(j+1)*9 for i in range(R)]
    else: # N == 0
        F[0] = [i for i in range(R)]
    #
    q = Articoli.objects.all()
    #
    if R>0:
        Risultato = []
        app1 = []
        for j in range(N+1):
            app1 = [(q[i].descrizione,q[i].codice, q[i].codice_a_barre,\
                     categorie_abbreviazioni[cat(q[i])][2],pos(q[i])) for i in F[j]]
            Risultato.append(app1)
            app1 = []
    else:
        Risultato = []
        app1 = []
        for j in range(N):
            app1 = [(q[i].descrizione,q[i].codice, q[i].codice_a_barre,\
                     categorie_abbreviazioni[cat(q[i])][2],pos(q[i])) for i in F[j]]
            Risultato.append(app1)
            app1 = []

    return render_to_response('listarticoli.html',
    {'datalista': data,
     'risultato': Risultato,
        })


@login_required
def articolidaordinare(request):
    """ Questo programma prepara la lista degli articoli da ordinare secondo il criterio
    Fornitore ---> suoi articoli da ordinare. Gli articoli sono da ordinare quando
    la giacenza è minore della scorta minima (che deve essere maggiore di zero; se fosse
    zero significherebbe che l'articolo non è più richiesto)
    """
    from  magazzino.models import Articoli,Fornitori

    data=datetime.now().strftime('%d-%m-%Y ore %H:%M')
    # Estrai tutti i fornitori
    z=Fornitori.objects.all().order_by('nome')
    d = {}
    for zz in z:
    # Estrai gli articoli da ordinare di ciascun fornitore individuato dal nome
        p = Articoli.objects.filter(fornitore__nome=zz.nome,giacenza__lte=F('scortaminima'), scortaminima__gt=0).order_by('giacenza','-scortaminima')
    # Se p non è nullo inserisci la voce nel dizionario d dove la chiave è il nome del fornitore
        if p:
            lista = []
            lista = [[t.codice,t.descrizione,str(t.giacenza),str(t.scortaminima)] for t in p]
            d[zz.nome] = lista
    return render_to_response('articolidaordinare.html',
    {'datalista': data,
     'risultato': d,
        })


@login_required
def articolidarestituire(request):
    """ Questo programma prepara la lista degli articoli da ordinare secondo il criterio
    Fornitore ---> suoi articoli da ordinare. Gli articoli sono da ordinare quando
    la giacenza è minore della scorta minima (che deve essere maggiore di zero; se fosse
    zero significherebbe che l'articolo non è più richiesto)
    """
    from  magazzino.models import Articoli,PazientiStorico,MovimentoOperazione,Movimentomag

    data=datetime.now().strftime('%d-%m-%Y ore %H:%M')
    # Estrai tutti i fornitori
    z=PazientiStorico.objects.filter(cessato=True).order_by('cognome','nome')
    d = {}
    for zz in z:
        y=MovimentoOperazione.objects.filter(paziente=zz)
        lista=[]
        for yy in y:
            w=Movimentomag.objects.filter(TipoMov=yy.pk)
            for ww in w:
                p=Articoli.objects.filter(codice=ww.codarticolo,restituzione=1)
    # Estrai gli articoli da ordinare di ciascun fornitore individuato dal nome
    # Se p non è nullo inserisci la voce nel dizionario d dove la chiave è il nome del fornitore
                if p:
                    lista = [[t.codice,t.descrizione,str(t.giacenza),str(t.scortaminima)] for t in p]
            d[zz.nome] = lista
    return render_to_response('articolidaordinare.html',
    {'datalista': data,
     'risultato': d,
        })
