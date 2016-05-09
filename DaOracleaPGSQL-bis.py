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
# Routine per salvataggio record di dettaglio in MovimentoOrdineDettaglio
def SalvaInArticoli(richiesta,codice,numero,totale):
    art = dettagli(id_ordine=richiesta,
            codarticolo=codice,
            numconfezioni=numero,
            totalepezzi=totale
            )
    art.save()
    return

#Routine per salvataggio record di dettaglio in ArticoliNonMagazzino
def SalvaAltro(richiesta, cod_AIFA,cod_Magazzino,farmaco,numero):
    altro = nonmagazzino(id_ordine=richiesta,
            codice_AIFA=cod_AIFA,
            codice=cod_Magazzino,
            descrizione=farmaco,
            confezioni=numero
            )
    altro.save()
    return

#Routine per la ricerca di farmaci uguali ma di diversi produttori presenti in articoli
#Restituisce in CodiceTrovato o False, se non ha trovato niente o il codice in Articoli
#dello stesso farmaco ma di altro produttore
def CercaRegex(testo):
    ArticoloTrovato = False
    print testo
    p = re.compile(r'^(\w+).*\*')
    m=p.match(testo)
    if not m:
        return ArticoloTrovato
    nome=p.findall(testo)[0]
    items=articoli.objects.filter(descrizione__startswith=nome)
    if items:
        testo=testo[m.end():]
        p = re.compile(r'\d+[ ]*(?=CPR)')
        if p.findall(testo):
            Ncpr1=p.findall(testo)[0]
            p = re.compile(r'\d+[ ]*(?=M?G)')
            MG1=p.findall(testo)[0]
            for b in items:
                z=b.descrizione
                p = re.compile(r'^(\w+).*\*')
                m=p.match(z)
                if m:
                    z=z[m.end():]
                    p = re.compile(r'\d+[ ]*(?=CPR)')
                    if p.findall(z):
                        Ncpr2=p.findall(z)[0]
                        p = re.compile(r'\d+[ ]*(?=M?G)')
                        MG2=p.findall(z)[0]
                        if (Ncpr1==Ncpr2 and MG1==MG2):
                            ArticoloTrovato = b
                            print(ArticoloTrovato)
                            return ArticoloTrovato
        else:
            p = re.compile(r'\d+[ ]*(?=F|FI|FL)')
            if p.findall(testo):
                Nfl1=p.findall(testo)[0]
                p = re.compile(r'\d+[ ]*(?=M?G)')
                MG1=p.findall(testo)[0]
                for b in items:
                    z=b.descrizione
                    p = re.compile(r'^(\w+).*\*')
                    m=p.match(z)
                    if m:
                        z=z[m.end():]
                        p = re.compile(r'\d+[ ]*(?=F|FI|FL)')
                        if p.findall(z):
                            Nfl2=p.findall(z)[0]
                            p = re.compile(r'\d+[ ]*(?=M?G)')
                            MG2=p.findall(z)[0]
                            if (Nfl1==Nfl2 and MG1==MG2):
                                ArticoloTrovato = b
                                print(ArticoloTrovato)
                                return ArticoloTrovato
    return ArticoloTrovato

t = con.cursor()
t.execute("select b.ID_PAT_HOSP,a.ID,a.DATA,a.ID_VISIT,a.ID_DOC,a.TIPO_CONSEGNA from noematica.magazzino_ordine a, noematica.magazzino_vista_ordini b WHERE a.ID=b.ID_ORDINE and b.DECEDUTO='N' and a.READED='N' ORDER BY a.ID")
ordine = t.fetchall()
if ordine: # Se esiste almeno un ordine, crea record ordine
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
# ll[0]= id_ordine, ll[1] = codicegalileo,ll[2]=codicemagazzino, ll[3]=numero confezioni
            try:
                f = articoli.objects.get(codice=ll[2])
                totale = ll[3]*f.quantita_conf
                SalvaInArticoli(ric,f,ll[3],totale)
    #            print("Paz.%s ord. %s Magazzino ==> %s: %s: %s quant. %s") % (ord[0], str(ord[1]),ll[2],f.codice, f.descrizione, str(ll[3]))
            except:
                try:
                    f = aifa.objects.get(id_aifa=ll[2])
                    a = articoli.objects.filter(descrizione=f.nome_farmaco)
                    if a:
                        totale = ll[3]*a[0].quantita_conf
                        SalvaInArticoli(ric,a[0],ll[3],totale)
                    else:
                        cod = CercaRegex(f.nome_farmaco)
                        if cod:
                            totale = ll[3]*cod.quantita_conf
                            SalvaInArticoli(ric,cod,ll[3],totale)
                        else:
                            SalvaAltro(ric, f.id_aifa,f.cod_magazzino,f.nome_farmaco,ll[3])
                except:
                    print("Ne in Magazzino ne in AIFA: %s, %s, %s,%s") % (ll[0],ll[1],ll[2],str(ll[3]))
# Metti come letto l'ordine
        cur = con.cursor()
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

