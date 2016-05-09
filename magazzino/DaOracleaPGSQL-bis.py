#Vai sotto la directory del progetto
import os
os.chdir('/home/victor/magazantea')

# Chiama django per l'esecuzione in uno script python
# equivale al comando "manage.py shell"
os.environ.setdefault('DJANGO_SETTINGS_MODULE','magazantea.settings')
import magazantea.settings
#######

from magazzino.models import Articoli as articoli, Pazienti as pazienti,FarmaciAIFA as aifa
from magazzino.models import MovimentoOrdine as ordini, MovimentoOrdineDettaglio as dettagli, MovimentoOrdineDettaglioNonMagazzino as nonmagazzino
from magazzino.decode32 import *
import datetime
import cx_Oracle
con = cx_Oracle.connect('magazzino', 'nl_magazzino', '46.28.3.78:/WBMDANT')

#Leggi da noematica.magazzino_vista_ordini i pazienti cessati
# e sistema la tabella pazienti in default
cur = con.cursor()
cur.execute("select ID_PAT_HOSP from noematica.magazzino_vista_ordini where DECEDUTO='Y'")
res=cur.fetchall()

if res:
# Routine per eliminare doppioni pazienti cessati
    def EliminaDoppioni():
        for i in res:
            if res.count(i) > 1:
                res.remove(i)
                EliminaDoppioni()
        return res
    EliminaDoppioni()
# Modifica tabella pazienti in default
    for dec in res:
        paz = pazienti.objects.get(codgalileo = dec[0])
        paz.cessato = True
        paz.save()

# Scarica  gli ordini non eseguiti da Oracle dalla tabella magazzino_ordine
t = con.cursor()
#t.execute("select * from noematica.magazzino_ordine where READED='N'")
t.execute("select b.ID_PAT_HOSP,a.ID,a.DATA,a.ID_VISIT,a.ID_DOC,a.TIPO_CONSEGNA from noematica.magazzino_ordine a, noematica.magazzino_vista_ordini b WHERE a.ID=b.ID_ORDINE and b.DECEDUTO='N' and a.READED='N' ORDER BY a.ID")

ordine = t.fetchall()
#Costruisci la stringa numerica da inserire nella clausola IN dell SQL
s=''
if ordine:
    s='('
    for i in [t[1] for t in ordine]:
        s+=str(i)+','
    s=s[:(len(s)-1)]+')'

#Leggi da noematica.magazzino_vista_ordini gli ordini ancora non evasi (READED='N')
# e mettili nella tabella magazzino_vista_ordini
if s:
    cur = con.cursor()
    cur.execute("select * from noematica.magazzino_vista_ordini " + "where ID_ORDINE IN "+s+ " and DECEDUTO='N'"+"order by ID_ORDINE")
    vista_ordini = cur.fetchall()

if vista_ordini:
# Sistemazione tabelle in dB Default
# Controllo tabella pazienti--- riscontro con  la query appena svolta da noematica.magazzino_vista_ordini
    for r in vista_ordini:
        try:
            print 'codgalileo esiste %s %s' %(r[2],r[3])
            p = pazienti.objects.get(codgalileo=r[0])
            p.cognome = r[2]
            p.nome = r[3]
            p.datanascita = r[4]
            p.luogo = r[5]
            p.cf = r[1]
            p.indirizzo = r[7]
            p.citta = r[9]
            p.cap = r[8]
            p.telefoni = r[10]
            p.contatti = r[11]
            p.cessato = r[12]
            p.save()
        except:
            print 'codgalileo NON esiste %s %s' %(r[2],r[3])
            patient = pazienti(cognome = r[2],
            nome = r[3],
            datanascita = r[4],
            luogo = r[5],
            cf = r[1],
            codgalileo = r[0],
            indirizzo = r[7],
            citta = r[9],
            cap = r[8],
            telefoni = r[10],
            contatti = r[11],
            cessato = r[12])
            patient.save()


# Scarica  gli ordini non eseguiti da Oracle dalla tabella magazzino_ordine
t = con.cursor()
t.execute("select * from noematica.magazzino_vista_lista where ID_ORDINE in " +s+ " ORDER BY ID_ORDINE")
lista = t.fetchall()

if ordine:
    for ord in ordine:
        rec = ordini(id_ordine=ord[1],
                        paziente=pazienti.objects.get(codgalileo=ord[0]),
                        data_emissione=ord[2],
                        visita=ord[3],
                        documento=ord[4],
                        consegna=ord[5],
                        eseguito=False)
        rec.save()
        for ls in lista:
                try:
                    a = articoli.objects.get(codice = ls[2])
                    print a
#                    d = dettagli(id_ordine = rec,
#                                codarticolo = a,
#                                numconfezioni = ls[3])
#                    d.save()
                except:
                    a = aifa.objects.get(id_aifa=ls[2])
                    print("AIFA --- %s cod.nostro %s nome: %s") % (a.id_aifa,a.cod_magazzino,a.nome_farmaco)
                    n = nonmagazzino(id_ordine=rec,
                                    codice_AIFA=ls[1],
                                    codice = decode32(ls[2]),
                                    descrizione = "BOH",
                                    confezioni = ls[3])
                    n.save()



    #
    # Cambia in Oracle lo stato dell'ordine da  READED='N' a READED='Y' (Ordine letto) in noematica.magazzino_ordine
    #
            c = con.cursor()
            c.execute("update noematica.magazzino_ordine set READED='Y' where ID="+str(r[0]))
            c.execute('COMMIT')


# Sistemazione tabelle in dB Default
# Controllo tabella pazienti--- riscontro con noematica.magazzino_vista_ordini
paz = ordini.objects.filter(readed='N')
# verifica se ciascun paziente in ordini è già registrato mediante id_pat_hosp in codgalileo di pazienti
for pz in paz:
    print 'inizio ciclo for pz in paz:'
    p = pazienti.objects.filter(codgalileo=pz.id_pat_hosp)
    # Se esiste codgalileo in pazienti verifica ciascuna voce di pazienti per eventuali aggiornamenti
    if p:
        print 'codgalileo esiste'
        p.cognome = pz.surname,
        p.nome = pz.name,
        p.datanascita = pz.birth_date,
        p.luogo = pz.birth_place
        p.cf = pz.fiscal_code,
        p.indirizzo = pz.street,
        p.citta = pz.city,
        p.cap = pz.zip_code,
        p.telefoni = pz.phone,
        p.contatti = pz.email,
        p.cessato = pz.deceduto
        p.save()
    else:
        print 'codgalileo NON esiste'
        patient = pazienti(cognome = pz.surname,
        nome = pz.name,
        datanascita = pz.birth_date,
        luogo = pz.birth_place,
        cf = pz.fiscal_code,
        codgalileo = pz.id_pat_hosp,
        indirizzo = pz.street,
        citta = pz.city,
        cap = pz.zip_code,
        telefoni = pz.phone,
        contatti = pz.email,
        cessato = pz.deceduto)
        patient.create()

ordini.objects.filter(readed='N').update(readed='Y')