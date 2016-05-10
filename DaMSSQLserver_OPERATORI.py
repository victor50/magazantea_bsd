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
from magazzino.models import Operatori as operatori

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
ID (0), Cognome (1), Nome (2), Titolo (3)
"""

cursor.execute("select * FROM XVW_OPERATORI_MAGAZ")

operator = cursor.fetchall()
for op in operator:
        q=operatori.objects.filter(cognome__startswith=op[1].upper(),nome__startswith=op[2])
        if len(q) > 0:
            q.update(id_spider=op[0], struttura=op[3])
        else:
            p = operatori(id_spider=op[0],
                cognome=op[1].upper(),
                nome= op[2],
                struttura=op[3]
                )
            p.save()
            print("Non trovato %s %s -aggiunto") %(op[1].upper(), op[2])
