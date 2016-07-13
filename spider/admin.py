from django.contrib import admin
from spider.models import *
# Register your models here.


class OrdineSpiderDettaglioInline(admin.TabularInline):
    model=OrdineSpiderDettaglio
    list_editable = ['codarticolo',]
    raw_id_fields = ('codarticolo',)
    readonly_fields= ['totalepezzi','collocazione']
    fields=(( 'id_ordine', 'codarticolo', 'numconfezioni', 'totalepezzi', 'collocazione','fatto'))
    extra = 1

class ArticoliSpiderNonMagazzinoInline(admin.TabularInline):
    model=ArticoliSpiderNonMagazzino
    readonly_fields= ['id_ordine',  'descrizione']
    fields=('descrizione', 'crea','numconfezioni')
    extra = 0

class OrdineSpiderOption(admin.ModelAdmin):
    list_per_page = 500
    readonly_fields = ['operatore','paziente','data_emissione',
'consegna',  'eseguito' ,'domicilio']
    search_fields=['paziente__cognome','paziente__nome']
    list_display = ('paziente', 'consegna','domicilio','data_emissione', 'eseguito')
    fields=(( 'data_emissione', 'paziente','operatore'),('domicilio'),('consegna','eseguito'))
 #   search_fields=['id_ordine','paziente']
    inlines=[OrdineSpiderDettaglioInline,ArticoliSpiderNonMagazzinoInline]
    order_by=['-id_ordine',]
    def domicilio(self,obj):
        testo = ('%s - %s'  %(obj.paziente.indirizzo,obj.paziente.citta))
        if obj.paziente.piano:
            testo += ' piano '+ obj.paziente.piano
        if obj.paziente.palazzina:
            testo += ' pal. '+ obj.paziente.palazzina
        if obj.paziente.nome_citofono:
            testo += ' citofonare '+ obj.paziente.nome_citofono
        if obj.paziente.telefoni:
            testo += ' tel. '+ obj.paziente.telefoni
        return testo
    domicilio.short_description='domicilio'
    def save_formset(self, request, form, formset, change):
       formset.save()
       Giacenze()

admin.site.register(OrdineSpider, OrdineSpiderOption)
