# Prima di eseguire questo programma da shell chiamare
# "pg_dump -Uantea -W magazzino > db.sql" per creare il file di partenza
import os
os.chdir('/home/victor/magazantea')

# Chiama django per l'esecuzione in uno script python
# equivale al comando "manage.py shell"
os.environ.setdefault('DJANGO_SETTINGS_MODULE','magazantea.settings')
import magazantea.settings
#######
from magazzino.models import Pazienti
import xlrd
book=xlrd.open_workbook('/home/victor/magazantea/pazienti.xls')


sh=book.sheet_by_name('pazienti')
c=0
for i in range(sh.nrows):
    c+=1
    Pazienti.objects.create(cognome=str(sh.cell_value(rowx=i, colx=0)), nome=str(sh.cell_value(rowx=i, colx=1)))
