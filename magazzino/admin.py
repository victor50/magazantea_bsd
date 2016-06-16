from django.contrib import admin
from django.contrib.auth.models import User
from django import forms
from magazzino.widgets import ForeignKeyRawIdWidget
from magazzino.models import *
from magazzino.actions import *
#
def chi(request, obj):
    myuser = unicode(request.user)
    return myuser

class SalvaModello(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        utente = unicode(request.user)
        if change:
            obj.modificato_da = utente
        else:
            obj.creato_da = utente
        obj.save()
    class Meta:
        abstract=True

class SalvaModelloInLine(admin.TabularInline):
    def save_form(self, request, form, change):
        obj = form.save(commit=False)
        utente = unicode(request.user)
        if change:
            obj.modificato_da = utente
        else:
            obj.creato_da = utente
        return obj
    class Meta:
        abstract=True



class FornitoriOption(SalvaModello):
    actions = ['delete_selected']
    search_fields=['nome','partita_iva','cf']
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    list_display = ('nome', 'indirizzo', 'cap', 'localita', 'provincia','nazione','telefono',
         'fax','partita_iva','cf')
    fields=(('creato_da','data_di_inserimento','modificato_da','data_di_modifica'),
             ('nome','telefono','fax'),('indirizzo', 'cap', 'localita',
             'provincia'),'nazione',('partita_iva','cf'),('email','sito_web'))
    order_by=['nome',]
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica']
    save_on_top=True


class ArticoliOption(SalvaModello):
    search_fields=['codice','descrizione']
    list_per_page = 1000
#    readonly_fields = ['giacenza','prezzo_scontato']
    list_display = ('descrizione','codice','categoria', 'giacenza', 'valore','unita_di_misura','quantita_conf')
    fields=(('codice','descrizione','categoria','giacenza'),('codice_iva', 'prezzo', 'sconto',
            'prezzo_scontato'),('codice_articolo_fornitore', 'unita_di_misura', 'quantita_conf','scortaminima'),'fornitore',
            ('idmagazzino', 'colarm', 'piano', 'altrorif1', 'altrorif2'),
            'note',  ('restituzione'))
    filter_horizontal = ['fornitore', ]
    list_filter=['categoria',]
#    date_hierarchy = 'data_di_inserimento'
    order_by= ['descrizione', ]
    actions = [export_Articoli_as_xls, Partitario_as_xls,StatisticheArticoli_as_xls]
    save_on_top=True
    def get_readonly_fields(self, request, obj=None):
        if obj: #This is the case when obj is already created i.e. it's an edit
            return ['codice','giacenza','prezzo_scontato','valore']
        else:
            return []


class MovimentomagInline(admin.TabularInline):
    raw_id_fields = ['codarticolo',]
    readonly_fields = ['totalepezzi','collocazione']
    fields = ('codarticolo', 'numerounita', 'numconfezioni', 'totalepezzi','collocazione')
    model=Movimentomag
    extra=5
    save_on_top=True

class ArticoliInline(admin.TabularInline):
    model=Articoli
    extra=5
    save_on_top=True

class MovimentomagOption(SalvaModello):
    list_per_page = 500
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica','totalepezzi','collocazione']
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica']
    list_display = ('codarticolo', 'numerounita', 'numconfezioni','totalepezzi')
    fields=(('creato_da','data_di_inserimento','modificato_da','data_di_modifica'),'codarticolo', ('numconfezioni', 'numerounita','totalepezzi',),'collocazione')
#    list_display_links=('codarticolo',)
#   inlines=[ArticoliInline,]
    save_on_top=True

class MovimentoOperazioneOption(SalvaModello):
    list_per_page = 500
    list_filter=['data_di_inserimento','operatore']
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica','data_movimento']
    list_display = ('segno', 'data_movimento', 'paziente','operatore')
    list_filter = ['segno', 'data_movimento', 'operatore',]
    fields=(('creato_da','modificato_da','data_di_inserimento','data_di_modifica'),('segno','data_movimento'),('paziente','operatore'))
    actions=[Stampa_Rapporto]
    inlines=[MovimentomagInline,]
    save_on_top=True
    order_by=['-data_movimento',]
#     def get_readonly_fields(self, request, obj=None):
#         if obj:
#             if obj.kit and obj.segno == -1: #This is the case when obj is already created i.e. it's an edit
#                 return self.readonly_fields.append('kit')
#             else:
#                 obj.kit = False
#                 return self.readonly_fields
#         else:
#             return self.readonly_fields
    def save_formset(self, request, form, formset, change):
        formset.save()
        Giacenze()

def nome(obj):
    return ("%s, %s" % (obj.cognome, obj.nome))
nome.short_description = 'nome'


class PazientiOption(SalvaModello):
    list_per_page = 500
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica','codgalileo','cessato','dotato_kit']
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica','data_chiusura']
    search_fields=['nome','cognome','codgalileo','cf']
    list_display = (nome,'datanascita','cf','codgalileo','inhospice','dotato_kit')
    fields=(('creato_da','modificato_da','data_di_inserimento','data_di_modifica'),
            ('cognome', 'nome','sesso'),
            ('datanascita', 'luogo', 'provincia'), ('cf','codgalileo'),
            ('indirizzo', 'citta', 'cap'), ('provincia_residenza'), ('telefoni','email'),('contatti'),
            ('altro_indirizzo','altra_citta','altro_cap'),('altra_provincia_residenza'),
            ('nome_citofono','palazzina','interno','scala','piano'),
            ('ascensore','parcheggio'),
            ('quartiere','municipio','asl'),
            ('cessato','data_chiusura', 'inhospice','rifantea','dotato_kit'))
    order_by= ['cognome', 'nome']
    save_on_top=True
#    def queryset(self, request):
#        """Mostra solo record pazienti non cessati."""
#        qs = super(PazientiOption, self).queryset(request)
###        return qs.filter(data_chiusura__isnull=True)
#        return qs.filter(cessato=False)


class PazientiStoricoOption(SalvaModello):
    list_per_page = 500
#    readonly_fields = ['creato_da','modificato_da']
    search_fields=['nome','cognome','codgalileo']
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica','codgalileo']
    list_filter=['creato_da','modificato_da','data_chiusura']
    list_display = (nome,'datanascita','cf','inhospice')
    fields=(('creato_da','modificato_da'),
            ('cognome', 'nome'),
            ('datanascita', 'luogo', 'provincia'), ('cf','codgalileo'),
            ('indirizzo', 'citta', 'cap'), ('telefoni','contatti'),
            ('cessato','data_chiusura', 'inhospice','rifantea'))
#    def get_readonly_fields(self, request, obj=None):
#        if unicode(request.user) != u'victor':
#            return ('creato_da','modificato_da','data_di_inserimento','data_di_modifica','cessato','data_chiusura','inhospice')
#        return ('creato_da','modificato_da','data_di_inserimento','data_di_modifica')
    order_by= ['cognome', 'nome']
    save_on_top=True


class OperatoriOption(SalvaModello):
    list_per_page = 500
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica']
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    search_fields=['nome','cognome']
    list_display = (nome,'struttura')
#    list_display = ('cognome','nome','struttura')
    fields=(('creato_da','modificato_da','data_di_inserimento','data_di_modifica'),
            ('cognome', 'nome'), 'struttura', 'telefoni',
             'contatti',)
    order_by= ['cognome','nome' ]
    save_on_top=True

class MovimentoFatturaDettaglioInline(admin.TabularInline):
    model=MovimentoFatturaDettaglio
    raw_id_fields = ['codarticolo',]
    readonly_fields= ['totalepezzi', 'prezzoscontato']
    exclude=['creato_da','modificato_da']
    fields=(('codarticolo','numerounita', 'numconfezioni','totalepezzi','prezzo', 'sconto','prezzoscontato'))
    extra=5
    save_on_top=True

class MovimentoFatturaInline(admin.TabularInline):
    model=MovimentoFattura
    extra=5
    save_on_top=True

class MovimentoFatturaDettaglioOption(SalvaModello):
    list_per_page = 500
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica']
    list_display = ('tipomov','codarticolo', 'numerounita', 'numconfezioni','totalepezzi',
                      'prezzo', 'sconto','prezzoscontato')
    fields=(('creato_da','data_di_inserimento','modificato_da','data_di_modifica'),('tipomov','codarticolo'), ('numerounita', 'numconfezioni','totalepezzi'),
               ('prezzo', 'sconto','prezzoscontato'))
    save_on_top=True

class MovimentoFatturaOption(SalvaModello):
    list_per_page = 500
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica']
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    list_display = ('fornitore', 'documento', 'numdoc','data_documento')
    fields=(('creato_da','modificato_da','data_di_inserimento','data_di_modifica'),
            ('fornitore'),('documento', 'data_documento','numdoc'))
    search_fields=['fornitore__nome','documento']
    actions=[Stampa_Rapp_Fattura]
    inlines=[MovimentoFatturaDettaglioInline,]
    save_on_top=True
    order_by=['-data_documento',]
    def save_formset(self, request, form, formset, change):
       formset.save()
       Giacenze()



class MovimentoOrdineDettaglioInline(admin.TabularInline):
    model=MovimentoOrdineDettaglio
    raw_id_fields = ['codarticolo',]
    readonly_fields= ['totalepezzi','collocazione']
    fields=(( 'id_ordine', 'codarticolo', 'numconfezioni', 'totalepezzi', 'collocazione','fatto'))
    extra = 1

class ArticoliNonMagazzinoInline(admin.TabularInline):
    model=ArticoliNonMagazzino
    readonly_fields= ['id_ordine', 'codice_AIFA', 'codice', 'descrizione']
    fields=('codice_AIFA', 'descrizione','codice', 'crea','confezioni')
    extra = 0

class MovimentoOrdineOption(SalvaModello):
    list_per_page = 500
    readonly_fields = [ 'id_ordine',  'paziente',  'data_emissione',  'visita',  'documento',  \
    'consegna',  'eseguito' ]
    search_fields=['paziente__cognome','paziente__nome', 'id_ordine']
    list_display = ( 'paziente','id_ordine', 'data_emissione', 'eseguito')
    fields=(( 'id_ordine', 'documento','data_emissione', 'visita'),('paziente'),('consegna'),('eseguito'))
 #   search_fields=['id_ordine','paziente']
    inlines=[MovimentoOrdineDettaglioInline,ArticoliNonMagazzinoInline]
    order_by=['-id_ordine',]
 #   def save_formset(self, request, form, formset, change):
 #      formset.save()
 #      Giacenze()
class FarmaciAIFAOption(admin.ModelAdmin):
    list_per_page = 1000
    readonly_fields = ['id_aifa','cod_magazzino','nome_farmaco']
    search_fields=['nome_farmaco','id_aifa','cod_magazzino']
    list_display = ('id_aifa','cod_magazzino','nome_farmaco','crea_farmaco')
    fields=(('id_aifa','cod_magazzino','nome_farmaco'),'crea_farmaco')
    order_by= ['nome_farmaco' ]
    save_on_top=True

class Kit_AnteaOption(SalvaModello):
    search_fields=['codarticolo__descrizione']
    list_per_page = 500
    raw_id_fields = ['codarticolo',]
    list_display = ('codarticolo', 'numerounita', 'numconfezioni','totalepezzi')
    fields=(('codarticolo'), ('numconfezioni', 'numerounita','totalepezzi'))
    order_by = ['codarticolo__descrizione',]
    save_on_top=True
#
admin.site.register(Kit_Antea,Kit_AnteaOption)
admin.site.register(Fornitori,FornitoriOption)
admin.site.register(Pazienti,PazientiOption)
admin.site.register(PazientiStorico,PazientiStoricoOption)
admin.site.register(Articoli,ArticoliOption)
admin.site.register(MovimentoOperazione,MovimentoOperazioneOption)
admin.site.register(Operatori,OperatoriOption)
admin.site.register(MovimentoFattura,MovimentoFatturaOption)
admin.site.register(FarmaciAIFA,FarmaciAIFAOption)
admin.site.register(MovimentoOrdine,MovimentoOrdineOption)
admin.site.register(Principi_Attivi)
admin.site.register(Forma_Farmaceutica)
admin.site.register(Tutti_Articoli)
