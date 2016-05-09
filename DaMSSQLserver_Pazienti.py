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
import os
import pymssql
from magazzino.models import Pazienti as pazienti
from datetime import datetime, date,timedelta
from django.db.models import Q


server = os.getenv("MY_SERVER")
user = os.getenv("MY_USER")
password = os.getenv("MY_PASSWORD")
database = os.getenv("MY_DATABASE")

conn = pymssql.connect(server, user, password, database)
cursor = conn.cursor()

"""
[IDAna,Cognome,Nome,CodiceFiscale,DataNascita,Sesso,LuogoNascita,Indirizzo,
Localita,CAP,Provincia,Telefono,Telefono2,Cellulare,Email,Cittadinanza,
FlagDecesso,DataDecesso,NomeCitofono,Municipio,Quartiere,Palazzina,Interno,
Scala,Piano,FlgAscensore,FlgParcheggio,IndirizzoAltraRes,CapAltraRes,
CittaAltraRes,ProvinciaAltraRes,ProvinciaNascita,DistrettoASL]
"""

conta1=conta2=conta3=0

# Determina una data antecedente di 15 gg
data_a_ritroso=(date.today() + timedelta(days=-15)).isoformat().replace("-","/") + ' 01:00:00.000'
#Query che seleziona i pazienti vivi o morti da non più di 15 gg
QUERY="SELECT * FROM XVW_PAZIENTI_MAGAZ WHERE (DataDecesso is null) OR (DataDecesso >= '"+ data_a_ritroso +"')"


#cursor.execute("SELECT * FROM XVW_PAZIENTI_MAGAZ")
cursor.execute(QUERY)

for pz in cursor:
    if pz[5] == 1:
        sex ='M'
    else:
        sex ='F'
    if pz[16] == 0:
        cess = False
        data_chius = None
    else:
        cess = True
        data_chius = pz[17]
    tel=''
    if pz[11]:
        tel = tel + pz[11]
    if pz[12]:
        tel = tel + ', '+ pz[12]
    if pz[13]:
        tel = tel + ', '+ pz[13]
    cod = 'XVW@'+'0'*(10-len(str(pz[0])))+str(pz[0])
    pazita =pazienti.objects.filter(cognome=pz[1],nome=pz[2], codgalileo__isnull=False)
    paz = pazienti.objects.filter(cognome=pz[1],nome=pz[2]).filter(Q(codgalileo='') | Q(codgalileo__isnull=True))
    if len(pazita) > 0:  #Se codgalileo è valorizzato (es. ITA@...,XVW@...)
        pz
        pazita.update(datanascita=pz[4],
			luogo=pz[6],
			cf=pz[3],
			indirizzo=pz[7],
			citta=pz[8],
			cap=pz[9],
			provincia=pz[10],
			telefoni=tel,
			email=pz[14],
			nome_citofono=pz[18],
			municipio=pz[19],
			quartiere=pz[20],
			palazzina=pz[21],
			interno=pz[22],
			scala=pz[23],
			piano=pz[24],
			ascensore=pz[25],
			parcheggio=pz[26],
			altro_indirizzo=pz[27],
			altro_cap=pz[28],
			altra_citta=pz[29],
			altra_provincia_residenza =pz[30],
			asl=pz[32],
			sesso=sex,
			cessato=cess,
			data_chiusura=data_chius)
        print("HO SOLO AGGIORNATO I CAMPI DIVERSI da cod")
        conta1 +=1
    elif len(paz) > 0:    #Se codgalileo non contiene nulla
        paz.update(codgalileo=cod,
			cognome=pz[1],
			nome=pz[2],
			datanascita=pz[4],
			luogo=pz[6],
			cf=pz[3],
			indirizzo=pz[7],
			citta=pz[8],
			cap=pz[9],
			provincia=pz[10],
			telefoni=tel,
			email=pz[14],
			nome_citofono=pz[18],
			municipio=pz[19],
			quartiere=pz[20],
			palazzina=pz[21],
			interno=pz[22],
			scala=pz[23],
			piano=pz[24],
			ascensore=pz[25],
			parcheggio=pz[26],
			altro_indirizzo=pz[27],
			altro_cap=pz[28],
			altra_citta=pz[29],
			altra_provincia_residenza =pz[30],
			asl=pz[32],
			sesso=sex,
			cessato=cess,
			data_chiusura=data_chius)
        print("TROVATO SENZA codgalileo CODIFICATO " + cod)
        conta2 +=1
    else:                 # il record non esiste
        patient = pazienti(codgalileo=cod,
			cognome=pz[1],
			nome=pz[2],
			datanascita=pz[4],
			luogo=pz[6],
			cf=pz[3],
			indirizzo=pz[7],
			citta=pz[8],
			cap=pz[9],
			provincia=pz[10],
			telefoni=tel,
			email=pz[14],
			nome_citofono=pz[18],
			municipio=pz[19],
			quartiere=pz[20],
			palazzina=pz[21],
			interno=pz[22],
			scala=pz[23],
			piano=pz[24],
			ascensore=pz[25],
			parcheggio=pz[26],
			altro_indirizzo=pz[27],
			altro_cap=pz[28],
			altra_citta=pz[29],
			altra_provincia_residenza =pz[30],
			asl=pz[32],
			sesso=sex,
			cessato=cess,
			data_chiusura=data_chius)
        patient.save()
        print('NUOVO  '+ cod)
        conta3 +=1
#
out_file = open("/home/victor/mylog.log","a")
TESTO= datetime.now().isoformat() + ' >>>> ' + str(conta1) + ';  '+ str(conta2) + '; *** NUOVI *** '+ str(conta3) + '\n'
out_file.write(TESTO)
out_file.close()
conn.close()



