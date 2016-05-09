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
from magazzino.models import Pazienti as pazienti
import datetime
import cx_Oracle
con = cx_Oracle.connect('magazzino', 'nl_magazzino', '46.28.3.78:/WBMDANT')

#Leggi da noematica.magazzino_vista_ordini i pazienti cessati
# e sistema la tabella pazienti in default
cur = con.cursor()
cur.execute("select * from magazzino_vista_pazienti")

#['ID_PAT_HOSP', 'FISCAL_CODE', 'SURNAME', 'NAME', 'BIRTH_DATE', 'BIRTH_PLACE',
# 'SEX', 'STREET', 'ZIP_CODE', 'CITY', 'PHONE', 'EMAIL', 'DECEDUTO',
# 'ID_VISIT_HOSP']

res=cur.fetchall()

if res:
    for pz in res:
        if pz[0][:4] == 'ITA@':
            paz = pazienti.objects.filter(codgalileo=pz[0])
            if paz:
                paz[0].cognome = pz[2]
                paz[0].nome = pz[3]
		paz[0].sesso =pz[6]
                paz[0].datanascita = pz[4]
                paz[0].luogo = pz[5]
                paz[0].cf = pz[1]
                paz[0].codgalileo = pz[0]
                paz[0].indirizzo = pz[7]
                paz[0].citta = pz[9]
                paz[0].cap = pz[8]
                paz[0].telefoni = pz[10]
                paz[0].contatti = pz[11]
                if pz[12] == 'N':
                    paz[0].cessato = 0
                else:
                    paz[0].cessato = 1
		    if not paz[0].data_chiusura:
			paz[0].data_chiusura = datetime.date.today()
                paz[0].save()
#                print pz[0], " UPDATE"
            else:
                if pz[12] == 'N':
                    cess = 0
                else:
                    cess = 1
                patient = pazienti(cognome = pz[2],
                nome = pz[3],
                datanascita = pz[4],
		sesso= pz[6],
                luogo = pz[5],
                cf = pz[1],
                codgalileo = pz[0],
                indirizzo = pz[7],
                citta = pz[9],
                cap = pz[8],
                telefoni = pz[10],
                contatti = pz[11],
                cessato = cess)
                patient.save()
#                print pz[0], " NUOVO RECORD"
