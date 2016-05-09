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
from magazzino.models import MovimentoOrdine as ordini, MovimentoOrdineDettaglio as dettagli, ArticoliNonMagazzino as nonmagazzino
from magazzino.decode32 import *
import datetime, re
import cx_Oracle
con = cx_Oracle.connect('magazzino', 'nl_magazzino', '46.28.3.78:/WBMDANT')

#############################################################################
#Caricamento in magazzino degli ordini
#############################################################################
t = con.cursor()
t.execute("select b.ID_PAT_HOSP,a.ID,a.DATA,a.ID_VISIT,a.ID_DOC,a.TIPO_CONSEGNA from noematica.magazzino_ordine a, noematica.magazzino_vista_ordini b WHERE a.ID=b.ID_ORDINE and b.DECEDUTO='N' and a.READED='N' ORDER BY a.ID")
ordine = t.fetchall()
if ordine: # Se esiste almeno un ordine
    for ord in ordine:
        cur = con.cursor()
        cur.execute("select * from noematica.magazzino_vista_lista " + "where ID_ORDINE="+str(ord[1]))
        lista = cur.fetchall()
        p = pazienti.objects.get(codgalileo=ord[0])
    # Crea ordine principale
        ric = ordini(id_ordine=ord[1],
                paziente=p,
                data_emissione=ord[2],
                visita=ord[3],
                documento=ord[4],
                consegna=ord[5],
                eseguito=False)
        ric.save()
    #    print("Paziente id %s, %s %s") % (str(p.pk),p.cognome, p.nome)
        for ll in lista:
# ll[0]= id_ordine, ll[1] = codicegalileo,ll[2]=codicemagazzino, ll[3]=quantità confezioni
            try:
                f = articoli.objects.get(codice=ll[2])
                totale = ll[3]*f.quantita_conf
                art = dettagli(id_ordine=ric,
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
                        art = dettagli(id_ordine=ric,
                            codarticolo=a[0],
                            numconfezioni=ll[3],
                            totalepezzi=totale
                            )
                        art.save()
                    else:
                        altro = nonmagazzino(id_ordine=ric,
                                codice_AIFA=f.id_aifa,
                                codice=f.cod_magazzino,
                                descrizione=f.nome_farmaco,
                                confezioni=ll[3]
                                )
                        altro.save()
    #                print("Paz.%s ord. %s AIFA ==> %s: %s: %s quant. %s") % (ord[0], str(ord[1]),ll[2],f.id_aifa, f.nome_farmaco, str(ll[3]))
                except:
                    print("Ne in Magazzino ne in AIFA: %s, %s, %s,%s") % (ll[0],ll[1],ll[2],str(ll[3]))
    # Metti come letto l'ordine
        cur.execute("UPDATE noematica.magazzino_ordine SET READED='Y' where ID="+str(ord[1]))
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

