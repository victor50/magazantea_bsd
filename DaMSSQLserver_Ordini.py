#-*- coding: utf-8 -*-


"""
Gli ordini al magazzino vengono divisi in due grandi gruppi:
1) Quelli che vengono ritirati direttamente in Hospice
2) Quelli con consegna a domicilio
"""

#Vai sotto la directory del progetto
import os
import django
os.chdir('/home/victor/magazantea')

# Chiama django per l'esecuzione in uno script python
# equivale al comando "manage.py shell"
os.environ.setdefault('DJANGO_SETTINGS_MODULE','magazantea.settings')
django.setup()
import magazantea.settings
#######

from datetime import datetime, date,timedelta
import pymssql

from magazzino.decode32 import *

from magazzino.models import Articoli as articoli, Pazienti as pazienti,FarmaciAIFA as aifa
from magazzino.models import Operatori as operatori
from spider.models import OrdineSpider as ordine, OrdineSpiderDettaglio as ordinedettaglio, ArticoliSpiderNonMagazzino as nonmagazzino

server = os.getenv("MY_SERVER")
user = os.getenv("MY_USER")
password = os.getenv("MY_PASSWORD")
database = os.getenv("MY_DATABASE")

con = pymssql.connect(server, user, password, database)
cursor = con.cursor()

#############################################################################
#Caricamento in magazzino degli ordini
#############################################################################

"""
ID (0), DataOraRegistrazione (1), IdAna (2), IDOperatore (3), DescOperatore (4), CodiceAifa (5),
Descrizione (6), Quantita (7), FlagLetto (8), ModoRitiro (9)
"""

#Ritiro in Hospice
cursor.execute("select * FROM XVW_ORDINI_MAGAZ WHERE FlagLetto=0 AND ModoRitiro='H' order by DataOraRegistrazione,IdAna")

richieste = cursor.fetchall()

if len(richieste) > 0: # Se esiste almeno un ordine
#Separa logicamente gli ordini con ritiro in Hospice
    H = {}
    b = []
    conta = 0
    pazien = richieste[0][2]
    for ord in richieste:
        ord
        if (ord[2] == pazien):
            b.append(ord[0])
            print "PASSO IF"
        else:
            H[conta] = b
            b = []
            conta += 1
            pazien = ord[2]
            b.append(ord[0])
            print "PASSO ELSE"
    H[conta] = b
    Ritira = {}
    for ric in richieste:
        Ritira[ric[0]] = ric[1:10]
#FINE Ritiro in Hospice
#
#Consegna a domicilio
cursor.execute("select * FROM XVW_ORDINI_MAGAZ WHERE FlagLetto=0 AND ModoRitiro='D' order by DataOraRegistrazione,IdAna")
richieste = cursor.fetchall()
if len(richieste) > 0: # Se esiste almeno un ordine
#Separa logicamente gli ordini con consegna a Domicilio
    D = {}
    b = []
    conta = 0
    pazien = richieste[0][2]
    for ord in richieste:
        ord
        if (ord[2] == pazien):
            b.append(ord[0])
            print "PASSO IF"
        else:
            D[conta] = b
            b = []
            conta += 1
            pazien = ord[2]
            b.append(ord[0])
            print "PASSO ELSE"
    D[conta] = b
    Consegna = {}
    for ric in richieste:
        Consegna[ric[0]] = ric[1:10]
#FINE Consegna a domicilio

for I in range(len(D)):
    for d in D[I]:
        d,Consegna[d]

cursor.execute("UPDATE XAR_ORDINI_FARMACIA SET FlagLetto=1 WHERE id=18")
con.commit()

if len(H) > 0:
    for i in range(len(H)):
# INIZIALIZZA VARIABILI
        primorecord = Ritira[H[i][0]]
# do sta per data e ora
        do = primorecord[0]
        do_min = datetime(do.year,do.month,do.day,do.hour,do.minute)
        do_max = do_min + timedelta(hours=+1)
        codpz = 'XVW@'+'0'*(10-len(str(primorecord[1])))+str(primorecord[1])
        codop = primorecord[2]
        o = operatori.objects.get(id_spider=codop)
        p = pazienti.objects.get(codgalileo=codpz)
        print('codpz = '+codpz)
        for ord in H[i]:
            R = Ritira[ord]
            codpz = 'XVW@'+'0'*(10-len(str(R[1])))+str(R[1])
            try:
                r = ordine.objects.get(paziente=p.pk, data_emissione__gte=do_min, data_emissione__lte=do_max)
                print("ESISTENTE"+ " pk= " + str(r.pk))
                if R[4][:2] == '$$':
                    code = R[4][2:]
                elif ((len(R[4]) > 0) and (R[4][:2] <> '$$')):
                    code = decode32(R[4])
                else:
                    code=None
                if code:
                    try:
                        a = articoli.objects.get(codice=code)
                    except:
                        code=None
                if code:
                    d = ordinedettaglio(id_ordine=r,
                        codarticolo=a,
                        numconfezioni=R[6])
                    d.save()
                else:
                    n = nonmagazzino(id_ordine=r,
                        descrizione=R[5],
                        numconfezioni=R[6])
                    n.save()
            except:
                r = ordine(paziente=p,
                    data_emissione=do_min,
                    operatore=o,
                    consegna='R',
                    eseguito=False)
                r.save()
                print('NUOVO REC ' +str(r.pk))
                if R[4][:2] == '$$':
                    code = R[4][2:]
                elif ((len(R[4]) > 0) and (R[4][:2] <> '$$')):
                    code = decode32(R[4])
                else:
                    code=None
                if code:
                    try:
                        a = articoli.objects.get(codice=code)
                    except:
                        code=None
                if code:
                    d = ordinedettaglio(id_ordine=r,
                        codarticolo=a,
                        numconfezioni=R[6])
                    d.save()
                else:
                    n = nonmagazzino(id_ordine=r,
                        descrizione=R[5],
                        numconfezioni=R[6])
                    n.save()





    p = pazienti.objects.get(codgalileo=codpz)
    if ord[8] == 'H':
        cons = 'R'
    else:
        cons = 'S'
# Crea ordini principale
    ric = ordini(id_ordini=ord[0],
            paziente=p,
            data_emissione=ord[1],
            consegna=cons,
            eseguito=False)
    ric.save()
#    print("Paziente id %s, %s %s") % (str(p.pk),p.cognome, p.nome)
    for ll in lista:
# ll[0]= id_ordini, ll[1] = codicegalileo,ll[2]=codicemagazzino, ll[3]=quantità confezioni
        try:
            f = articoli.objects.get(codice=ll[2])
            totale = ll[3]*f.quantita_conf
            art = dettagli(id_ordini=ric,
                    codarticolo=f,
                    numconfezioni=ll[3],
                    totalepezzi=totale
                    )
            art.save()
#            print("Paz.%s ord. %s Magazzino ==> %s: %s: %s quant. %s") % (ord[0], str(ord[1]),ll[2],f.codice, f.descrizione, str(ll[3]))
        except:
            try:
                f = aifa.objects.get(id_aifa=ll[2])
                a = articoli.objects.filter(descrizione=f.nome_farmaco)
                if a:
                    totale = ll[3]*a[0].quantita_conf
                    art = dettagli(id_ordini=ric,
                        codarticolo=a[0],
                        numconfezioni=ll[3],
                        totalepezzi=totale
                        )
                    art.save()
                else:
                    altro = nonmagazzino(id_ordini=ric,
                            codice_AIFA=f.id_aifa,
                            codice=f.cod_magazzino,
                            descrizione=f.nome_farmaco,
                            confezioni=ll[3]
                            )
                    altro.save()
#                print("Paz.%s ord. %s AIFA ==> %s: %s: %s quant. %s") % (ord[0], str(ord[1]),ll[2],f.id_aifa, f.nome_farmaco, str(ll[3]))
            except:
                print("Ne in Magazzino ne in AIFA: %s, %s, %s,%s") % (ll[0],ll[1],ll[2],str(ll[3]))
    # Metti come letto l'ordini
        cur.execute("UPDATE noematica.magazzino_ordini SET READED='Y' where ID="+str(ord[1]))
        cur.execute("COMMIT")

########################################################################################################
########################################################################################################
########################################################################################################
#if res:
## Routine per eliminare doppioni pazienti cessati
#    def EliminaDoppioni():
#        for i in res:
#            if res.count(i) > 1:
#                res.remove(i)
#                EliminaDoppioni()
#        return res
#    EliminaDoppioni()
## Modifica tabella pazienti in default

