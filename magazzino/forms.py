from django.forms import ModelForm,CharField
from magazzino.models import *

class ArticoliForm(ModelForm):
    class Meta:
        model = Articoli
        localized_fields = ('prezzo','prezzo_scontato','sconto')

class MovimentomagForm(ModelForm):
    creato_da = CharField(max_length = 20)
    modificato_da = CharField(max_length = 20)
    class Meta:
        model = Movimentomag
