#Vai sotto la directory del progetto
import os
os.chdir('/home/victor/magazantea')

# Chiama django per l'esecuzione in uno script python
# equivale al comando "manage.py shell"
os.environ.setdefault('DJANGO_SETTINGS_MODULE','magazantea.settings')
import magazantea.settings
#######

from magazzino.models import Articoli
from magazantea.settings import MEDIA_ROOT
from magazzino.barcode import *

#Seleziona tutti gli articoli
q=Articoli.objects.all()

#Per ogni record crea da 'codice_a_barre' l'immagine del codice a barre e mettilo in /media
for a in q:
    nomefile= str(a.codice_a_barre)
    CreaCodiceBarra(a.codice,nomefile)


