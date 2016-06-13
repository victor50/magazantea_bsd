#-*- coding: utf-8 -*-

"""
Gli ordini al magazzino vengono divisi in due grandi gruppi:
1) Quelli che vengono ritirati direttamente in Hospice
2) Quelli con consegna a domicilio
Dunque se un paziente ha sua articoli da ritirare direttamente in Hospice
che da ricevere a domicilio compariranno due ordini distinti
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

from comune.prog_servizio import *

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

H = D = {}

if len(richieste) > 0: # Se esiste almeno un ordine
#Separa logicamente gli ordini con ritiro in Hospice
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
'''
Sistemazione delle richieste di articoli che verranno
ritirati direttamente in Hospice
'''
if len(H) > 0:
    for i in range(len(H)):
# INIZIALIZZA VARIABILI
        primorecord = Ritira[H[i][0]]
# 'do' sta per data e ora
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
                r = ordine.objects.get(paziente=p.pk, data_emissione__gte=do_min, data_emissione__lte=do_max, consegna='R')
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
# Impostazione di FlagLetto in archivio farmaci a Letto
            cursor.execute("UPDATE XAR_ORDINI_FARMACIA SET FlagLetto=1 WHERE id="+str(ord))
            con.commit()

'''
Sistemazione delle richieste di articoli che dovranno
essere consegnati al domicilio del paziente
'''

if len(D) > 0:
    for i in range(len(D)):
# INIZIALIZZA VARIABILI
        primorecord = Consegna[D[i][0]]
# 'do' sta per data e ora
        do = primorecord[0]
        do_min = datetime(do.year,do.month,do.day,do.hour,do.minute)
        do_max = do_min + timedelta(hours=+1)
        codpz = 'XVW@'+'0'*(10-len(str(primorecord[1])))+str(primorecord[1])
        codop = primorecord[2]
        o = operatori.objects.get(id_spider=codop)
        p = pazienti.objects.get(codgalileo=codpz)
        print('codpz = '+codpz)
        for ord in D[i]:
            C = Consegna[ord]
            codpz = 'XVW@'+'0'*(10-len(str(C[1])))+str(C[1])
            try:
                r = ordine.objects.get(paziente=p.pk, data_emissione__gte=do_min, data_emissione__lte=do_max, consegna='S')
                print("ESISTENTE"+ " pk= " + str(r.pk))
                if C[4][:2] == '$$':
                    code = C[4][2:]
                elif ((len(C[4]) > 0) and (C[4][:2] <> '$$')):
                    code = decode32(C[4])
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
                        numconfezioni=C[6])
                    d.save()
                else:
                    n = nonmagazzino(id_ordine=r,
                        descrizione=C[5],
                        numconfezioni=C[6])
                    n.save()
            except:
                r = ordine(paziente=p,
                    data_emissione=do_min,
                    operatore=o,
                    consegna='S',
                    eseguito=False)
                r.save()
                print('NUOVO REC ' +str(r.pk))
                if C[4][:2] == '$$':
                    code = C[4][2:]
                elif ((len(C[4]) > 0) and (C[4][:2] <> '$$')):
                    code = decode32(C[4])
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
                        numconfezioni=C[6])
                    d.save()
                else:
                    n = nonmagazzino(id_ordine=r,
                        descrizione=C[5],
                        numconfezioni=C[6])
                    n.save()
# Impostazione di FlagLetto in archivio farmaci a Letto
            cursor.execute("UPDATE XAR_ORDINI_FARMACIA SET FlagLetto=1 WHERE id="+str(ord))
            con.commit()
