#-*- coding: utf-8 -*-

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

from magazzino.models import Articoli as articoli, Pazienti as pazienti,FarmaciAIFA as aifa
from magazzino.models import Operatori as operatori, MovimentoOrdine as ordini, MovimentoOrdineDettaglio as dettagli
from magazzino.models import ArticoliNonMagazzino as nonmagazzino
from magazzino.decode32 import *
from datetime import datetime, date,timedelta

import pymssql

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

cursor.execute("select * FROM XVW_ORDINI_MAGAZ order by DataOraRegistrazione,IdAna")

richieste = cursor.fetchall()

if len(richieste) > 0: # Se esiste almeno un ordine
#Separa logicamente gli ordini
    a= {}
    b = []
    conta = 0
    pazien = richieste[0][2]
    ritiro = richieste[0][9]
    for ord in richieste:
        ord
        if (ord[2] == pazien and ord[9] == ritiro):
            b.append(ord[0])
            print "PASSO IF"
        else:
            a[conta] = b
            b = []
            conta += 1
            pazien = ord[2]
            ritiro = ord[9]
            b.append(ord[0])
            print "PASSO ELSE"
    a[conta] = b



    for ord in richieste:
        codpz = 'XVW@'+'0'*(10-len(str(ord[2])))+str(ord[2])
        if ord[4][:2] == '$$':
            code = ord[4][2:]
        else:
            code = decode32(ord[4])

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

