from django.contrib import admin
from spider.models import *
# Register your models here.

class OrdineSpiderDettaglioInline(admin.TabularInline):
    model=OrdineSpiderDettaglio
    raw_id_fields = ['codarticolo',]
    readonly_fields= ['totalepezzi','collocazione']
    fields=(( 'id_ordine', 'codarticolo', 'numconfezioni', 'totalepezzi', 'collocazione','fatto'))
    extra = 1

class ArticoliSpiderNonMagazzinoInline(admin.TabularInline):
    model=ArticoliSpiderNonMagazzino
    readonly_fields= ['id_ordine', 'codice_AIFA', 'codice', 'descrizione']
    fields=('codice_AIFA', 'descrizione','codice', 'crea','confezioni')
    extra = 0

class OrdineSpiderOption(admin.ModelAdmin):
    list_per_page = 500
#    readonly_fields = [ 'paziente','data_emissione',  'consegna',  'eseguito' ]
    search_fields=['paziente__cognome','paziente__nome']
    list_display = ( 'paziente', 'data_emissione', 'eseguito')
    fields=(( 'data_emissione', 'paziente','operatore'),('consegna'),('eseguito'))
 #   search_fields=['id_ordine','paziente']
    inlines=[OrdineSpiderDettaglioInline,ArticoliSpiderNonMagazzinoInline]
    order_by=['-id_ordine',]
 #   def save_formset(self, request, form, formset, change):
 #      formset.save()
 #      Giacenze()
admin.site.register(OrdineSpider, OrdineSpiderOption)
