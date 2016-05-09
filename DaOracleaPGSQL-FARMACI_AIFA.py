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
from magazzino.models import FarmaciAIFA as farmaci
from magazzino.decode32 import decode32
import datetime
import cx_Oracle
con = cx_Oracle.connect('magazzino', 'nl_magazzino', '46.28.3.78:/WBMDANT')

#Leggi da noematica.magazzino_vista_ordini i pazienti cessati
# e sistema la tabella pazienti in default
cur = con.cursor()
cur.execute("select * from magazzino_farmaci_aifa")

res=cur.fetchall()
for r in res:
    try:
        farm=farmaci.objects.get(id_aifa=r[0])
    except:
        f = farmaci(id_aifa= r[0],
                    cod_magazzino=decode32(r[0]),
                    nome_farmaco=r[1])
        f.save()
con.close()