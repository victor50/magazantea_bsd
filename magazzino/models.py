#-*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import pre_delete,post_delete,post_save,pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache
from django_cache_manager.cache_manager import CacheManager
from comune.prog_servizio import decode32
from comune.signals import *
from comune.prog_servizio import *
from magazzino.barcode import CreaCodiceBarra
from magazantea.settings import MEDIA_ROOT

from decimal import Decimal


categorie_abbreviazioni = ((1, 'Farmaci','FA'), (2, 'Dispositivi sanitari','DS'),\
     (3, 'Generale','GE'),  (4, 'Materiale di consumo','MC'), (5, 'Medicazioni','ME'),)

categoria = [(cat[0],cat[1]) for cat in categorie_abbreviazioni]



magazzino = ((10,'1'),(20,'2'),(30,'3'),(40,'CARRELLO EMERGENZA'),(45,'CASETTA'),(50,'FRIGORIFERO'), \
             (60,'HOSPICE'),(70,'MEDICHERIA'),)

posizione = ((1,''),  (2, '01'),  (3, '02'),  (4, '03'),  (5, '04'),  (6, '05'), \
  (7, '06'),  (8, '07'),  (9, '08'),  (10, '09'),  (11, '10'),  \
  (12, '11'),  (13, '12'),  (14, '13'),  (15, '14'),  (16, '15'),  \
  (17, '16'),  (18, '17'),  (19, '18'),  (20, '19'),  (21, '20'),  \
  (22, 'A'),  (23, 'B'),  (24, 'C'),  (25, 'D'),  (26, 'E'),  \
  (27, 'F'),  (28, 'G'),  (29, 'H'),  (30, 'I'),  (31, 'J'),  \
  (32, 'K'),  (33, 'L'),  (34, 'M'),  (35, 'N'),  (36, 'O'),  \
  (37, 'P'),  (38, 'Q'),  (39, 'R'),  (40, 'S'), (41,'T'), (42, 'U'),  \
  (43, 'V'),  (44, 'W'),  (45, 'X'),  (46, 'Y'),  (47, 'Z'),)

codici_IVA = ((10,'IVA 10%'), (20,'IVA 20%'),(21,'IVA 21%'),(22,'IVA 22%'), \
            (4,'IVA 4%'),(100,'Fuori campo IVA'),)



unita_misura = ((6, 'Bottiglie'), (12, 'Bustine'), (10, 'Capsule'), \
             (4, 'Compresse'), (8, 'Fiale'), (2, 'Flaconi'),\
             (11, 'Kit'), (1, 'Pezzi'), (13, 'Sacca'), \
             (7, 'Scatolette'), (5, 'Supposte'), (14,'Tubo'),)

tipodocumento = ((1,u'BOLLA'),(2,u'FATTURA'), (3,u'LISTA SINTESI'))

mod_consegna = (('S',u'SPEDIRE'),('R',u'RITIRA'))


class DateUtenti(models.Model):
    data_di_inserimento = models.DateTimeField(auto_now_add=True,null=True, db_column='datains', blank=True,verbose_name='data inserimento')
    data_di_modifica = models.DateTimeField(auto_now=True,null=True, db_column='datamod', blank=True,verbose_name='data modifica')
    creato_da = models.CharField(max_length=15,null=True,blank=True)
    modificato_da = models.CharField(max_length=15,null=True,blank=True)
    class Meta:
        abstract=True


class Fornitori(DateUtenti):
    nome = models.CharField(max_length=150, db_column='nome', db_index=True)
    indirizzo = models.CharField(max_length=255, db_column='indirizzo', blank=True,null=True)
    cap = models.CharField(max_length=18, db_column='cap', blank=True,null=True)
    localita = models.CharField(max_length=150, db_column='localita', blank=True,null=True)
    provincia = models.CharField(max_length=12, db_column='prov', blank=True,null=True)
    nazione = models.CharField(max_length=150, db_column='nazione', blank=True,default='ITALIA',null=True)
    telefono = models.CharField(max_length=90, db_column='telefono', blank=True,null=True)
    fax = models.CharField(max_length=90, db_column='fax', blank=True,null=True)
    cellulare = models.CharField(max_length=90, db_column='cellulare', blank=True,null=True)
    email = models.EmailField(max_length=75, db_column='email', blank=True,null=True)
    sito_web = models.URLField(max_length=250, db_column='sito_web', blank=True,null=True)
    partita_iva = models.CharField(max_length=15, db_column='piva', blank=True,verbose_name="p.IVA",null=True)
    cf = models.CharField(max_length=15, db_column='cf', blank=True,verbose_name="Cod.Fiscale",null=True)
    note = models.TextField(db_column='note', blank=True,null=True)
    def __unicode__(self):
        return self.nome
    def save(self):
        super(Fornitori,self).save()
    class Meta:
        db_table = u'fornitori'
        verbose_name_plural = "Fornitori"
        ordering=['nome']




class Pazienti(DateUtenti):
    cognome = models.CharField(max_length=60, db_column='cognome',  db_index=True)
    nome = models.CharField(max_length=60, db_column='nome',  db_index=True)
    datanascita = models.DateField(verbose_name='Data di Nascita', null=True, blank=True)
    luogo = models.CharField(max_length=90, verbose_name='Luogo di Nascita', blank=True,null=True)
    provincia = models.CharField(max_length=25, db_column='provincia', blank=True,null=True)
    cf = models.CharField(max_length=48, verbose_name='Codice Fiscale', blank=True,null=True)
    codgalileo = models.CharField(max_length=63, verbose_name='Codice Spider', null=True, blank=True,db_index=True)
    indirizzo = models.CharField(max_length=150, db_column='indirizzo', null=True, blank=True)
    citta = models.CharField(max_length=120, db_column='citta', verbose_name='Città',null=True, blank=True)
    cap = models.CharField(max_length=15, db_column='cap', null=True, blank=True)
    provincia_residenza = models.CharField(max_length=25, db_column='provresidenza', blank=True,null=True)
    sesso = models.CharField(max_length=1, db_column='sesso',verbose_name='Sesso', blank=True,null=True)
    altro_indirizzo = models.CharField(max_length=150, db_column='altroindirizzo',verbose_name='Indirizzo Domicilio', null=True, blank=True)
    altra_citta = models.CharField(max_length=120, db_column='altracitta',verbose_name='Città dom.', null=True, blank=True)
    altro_cap = models.CharField(max_length=15, db_column='altrocap', verbose_name='Cap dom.',null=True, blank=True)
    altra_provincia_residenza = models.CharField(max_length=25, db_column='provresidenza2', verbose_name='Provincia dom.',blank=True,null=True)
    sesso = models.CharField(max_length=1, db_column='sesso',verbose_name='Sesso', blank=True,null=True)
    telefoni = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    contatti = models.TextField(db_column='contatti', null=True, blank=True)
    nome_citofono = models.CharField(max_length=150, db_column='nomecitofono',null=True, blank=True)
    municipio = models.CharField(max_length=50, db_column='municipio',null=True, blank=True)
    quartiere = models.CharField(max_length=50, db_column='quartiere',null=True, blank=True)
    palazzina = models.CharField(max_length=50, db_column='palazzina',null=True, blank=True)
    interno = models.CharField(max_length=10, db_column='interno',null=True, blank=True)
    scala = models.CharField(max_length=12, db_column='scala',null=True, blank=True)
    piano = models.CharField(max_length=12, db_column='piano',null=True, blank=True)
    ascensore = models.BooleanField(default=True, db_column="ascensore")
    parcheggio = models.BooleanField(default=False, db_column="parcheggio")
    asl = models.CharField(max_length=10, db_column='asl',null=True, blank=True)
    rifantea = models.CharField(max_length=90, db_column='rifantea', verbose_name='Rif. Antea', blank=True,null=True)
    cessato = models.BooleanField(default=False, db_column="cessato")
    inhospice = models.BooleanField(default=False, db_column="inhospice",verbose_name='Curato in Hospice')
    data_chiusura = models.DateField(null=True,blank=True)
    dotato_kit = models.BooleanField(default=False, db_column="dotato_kit")
    # nrec_kit rappresenta il numero del record di movimentooperazione in cui si è richiesto il kit
    nrec_kit = models.IntegerField(db_column='nrec_kit', verbose_name='Riferimento record', null=True, blank=True, default=0)
#
    objects = CacheManager()
#
    def __unicode__(self):
        return u"%s, %s" % (self.cognome, self.nome)
    class Meta:
        db_table = u'pazienti'
        verbose_name_plural = "Pazienti ANTEA"
        ordering=['cognome', 'nome']

class PazientiStorico(Pazienti):
    class Meta:
        proxy=True
        verbose_name_plural = "Pazienti ANTEA --> Storico"



class Operatori(DateUtenti):
    cognome = models.CharField(max_length=60, db_column='cognome', db_index=True)
    nome = models.CharField(max_length=60, db_column='nome', blank=True, db_index=True)
    struttura = models.CharField(max_length=90, verbose_name='Qualifica',
                null=True, blank=True)
    telefoni = models.CharField(max_length=150, null=True, blank=True)
    contatti = models.TextField(db_column='contatti', null=True, blank=True)
    id_spider = models.IntegerField(db_index=True, unique=True,default=1, db_column='id_spider', verbose_name='ID Spider')
#
    objects = CacheManager()
#
    def __unicode__(self):
        return u"%s, %s" % (self.cognome, self.nome)
    class Meta:
        db_table = u'operatori'
        verbose_name_plural = "Operatori ANTEA"
        ordering=['cognome', 'nome']


class Articoli(DateUtenti):
    codice = models.CharField(primary_key=True,db_index=True,unique=True,max_length=20,db_column='codice')
    descrizione = models.CharField(max_length=255, db_column='descrizione', db_index=True, unique=False)
    fornitore = models.ManyToManyField(Fornitori)
    codice_articolo_fornitore = models.CharField(max_length=60, db_column='codiceartfor', blank=True,null=True)
    categoria = models.IntegerField(choices=categoria, db_column='categoria',default=1)
    codice_iva = models.IntegerField(choices=codici_IVA, default='22',db_column='codiceiva', verbose_name='Codice IVA')
#    prezzo = models.FloatField(null=True, db_column='prezzo',default=0.0, blank=True)
    prezzo = models.DecimalField(decimal_places=5, max_digits=14, db_column='prezzo',
              default=0.0,verbose_name='Prezzo unitario')
    sconto = models.FloatField(null=True, db_column='sconto', default=0.0,blank=True)
#    prezzo_scontato = models.FloatField(db_column='prezzo_scontato', blank=True,null=True,verbose_name='Prezzo Scontato')
    prezzo_scontato = models.DecimalField(decimal_places=5, max_digits=14, db_column='prezzo_scontato',
              default=0.0,verbose_name='Prezzo Scontato')
    unita_di_misura = models.IntegerField(choices=unita_misura, db_column='unita_di_misura_id',null=True,blank=True,verbose_name=u'Unità di misura')
    scortaminima = models.IntegerField(null=True, db_column='scortaminima', blank=True,verbose_name='Scorta minima')
    idmagazzino = models.IntegerField(choices=magazzino, default=10, db_column='idmagazzino',
                     verbose_name='Magazzino')
    colarm = models.IntegerField(choices=posizione, default=1,db_column='colarm_id',verbose_name=u'Stanza')
    piano = models.IntegerField(choices=posizione, default=1,db_column='piano_id',verbose_name='Colonna')
    altrorif1 = models.IntegerField(choices=posizione, default=1,db_column='altrorif1_id', verbose_name='Ripiano')
    altrorif2 = models.IntegerField(choices=posizione, default=1,db_column='altrorif2_id',verbose_name='Altro')
    note = models.TextField(db_column='note', blank=True, null=True)
    quantita_conf = models.IntegerField(db_column='quantitaxconf', default=0,verbose_name=u'Quantità per confezione')
    restituzione = models.IntegerField(choices=((0,'No'),(1,u'Sì')),default=0)
    giacenza=models.IntegerField(db_column='giacenza', verbose_name='Giacenza di magazzino', default=0)
#
    objects = CacheManager()
#
    @property
    def valore(self):
        return (round(self.giacenza*self.prezzo_scontato,3))
#
    @property
    def codice_a_barre(self):
        self.codice = self.codice.strip()
        cod= self.codice.replace(" ", "_").replace("/","_").replace(".","_")
        return (str(cod)+ '.png')
#
#
    def save(self):
#   Elimina gli spazi prima e dopo sia in codice che in descrizione
        self.descrizione = self.descrizione.strip()
        self.descrizione = self.descrizione.replace('|','I')
        self.descrizione = self.descrizione.replace('"',' ')
        self.codice = self.codice.replace('|','I')
        self.codice = self.codice.replace('"','')
        self.codice = self.codice.replace(' ','')
        self.codice = self.codice.strip()
        self.codice = self.codice.upper()
#   Calcola prezzo scontato
        self.prezzo_scontato = float(self.prezzo)*(1-self.sconto/100)
        super(Articoli,self).save()
        CreaCodiceBarra(self.codice,self.codice_a_barre)
        return
#
    def __unicode__(self):
        return self.descrizione
    class Meta:
        db_table = u'articoli'
        verbose_name_plural = "Articoli"
        ordering=['descrizione']

pre_delete.connect(elimina_file_img, sender=Articoli)
#m2m_changed.connect(m2m_ModificaArticoliInICEC, sender=Articoli.fornitore.through)



class MovimentoOperazione(DateUtenti):
    segno = models.IntegerField(choices=((-2, u'ARTICOLI SCADUTI'),(-1,u'ARTICOLI IN USCITA'),(1,u'ARTICOLI IN ENTRATA')),
            default=-1,verbose_name=u'OPERAZIONE')
#    data_movimento=models.DateTimeField(db_index=True)
    data_movimento=models.DateTimeField(auto_now_add=True,db_index=True)
    paziente=models.ForeignKey(Pazienti,default=1)
    operatore=models.ForeignKey(Operatori,default=1)
#    kit = models.BooleanField(default=False, db_column="kit",verbose_name='Fornire kit')
    @property
    def id_operazione(self):
        return self.pk
    def __unicode__(self):
        return u"paziente: %s; operatore: %s" % (self.paziente, self.operatore)
    class Meta:
        db_table = u'movimentooperazione'
        verbose_name_plural = "Magazzino ANTEA Entrata/Uscita"
        verbose_name = "Movimento"
        ordering=['-data_movimento']

post_delete.connect(Elimina_Movimento, sender=MovimentoOperazione)

class Movimentomag(DateUtenti):
    tipomov = models.ForeignKey(MovimentoOperazione,verbose_name='Magazzino Dettaglio Movimento')
    codarticolo = models.ForeignKey(Articoli, db_index=True,verbose_name='Articolo')
    numconfezioni = models.IntegerField(null=True, db_column='numconfezioni',
                       blank=True,default=None,verbose_name='Num. Confezioni')
    numerounita = models.IntegerField(db_column='numerounita',blank=True,default=None,
                       verbose_name=u'Numero Unità')
    totalepezzi = models.IntegerField(null=True, db_column='totalepezzi',
                       default=0,verbose_name=u'Totale Unità',blank=True)
    @property
    def collocazione(self):
        for m in magazzino:
            if m[0] == self.codarticolo.idmagazzino:
                break
        pos = (m[1] + ':' + posizione[self.codarticolo.colarm-1][1] + '-' + posizione[self.codarticolo.piano-1][1] + '-' + posizione[self.codarticolo.altrorif1-1][1])
        return pos
 #
    def save(self):
        f=Articoli.objects.get(descrizione=self.codarticolo)
        p=MovimentoOperazione.objects.get(pk=self.tipomov_id)
        if (f.codice == '_KIT_'): # SE HAI CHIESTO KIT ED IL PAZIENTE NON LO HA
            richiesta_kit = True
        else:
            richiesta_kit = False
        if (p.paziente.dotato_kit): #SE il paziente ha avuto il kit non è bisognoso
            paziente_bisognoso = False
        else:
            paziente_bisognoso = True
        if not self.numconfezioni:
            self.numconfezioni = 0
        if not self.numerounita:
            self.numerounita = 0
        self.totalepezzi = self.numconfezioni*f.quantita_conf+self.numerounita
        self.creato_da=p.creato_da
        self.modificato_da=p.modificato_da
        super(Movimentomag,self).save()
        if (richiesta_kit and paziente_bisognoso and p.segno < 0) or (richiesta_kit and not paziente_bisognoso and p.segno > 0):
            kk = Kit_Antea.objects.all()
            for k in kk:
                new_mm = Movimentomag(codarticolo = k.codarticolo, tipomov_id=p.pk, \
                    numconfezioni=k.numconfezioni, numerounita=k.numerounita, \
                    totalepezzi = k.totalepezzi,creato_da=p.creato_da, modificato_da=p.modificato_da)
                new_mm.save()
            mm = Movimentomag.objects.filter(codarticolo_id='_KIT_',tipomov_id=p.pk)
            for m in mm:
                m.delete()
            p.paziente.dotato_kit=True
            p.paziente.nrec_kit = p.pk
            p.paziente.save()
        else:
            mm = Movimentomag.objects.filter(codarticolo_id='_KIT_',tipomov_id=p.pk)
            for m in mm:
                m.delete()
    def __unicode__(self):
        return self.codarticolo.descrizione
    class Meta:
        db_table = u'movimentomag'
        verbose_name_plural = "Dettaglio Movimenti ANTEA senza bolla o fattura"
        ordering=['data_di_inserimento', ]

post_delete.connect(TotaliGiacenze, sender=Movimentomag)


class MovimentoFattura(DateUtenti):
    fornitore=models.ForeignKey(Fornitori, db_index=True)
    documento = models.IntegerField(choices=tipodocumento, default=1,verbose_name=u'Documento')
    numdoc=models.CharField(max_length=15, db_column='numdoc',blank=True,verbose_name="Num. Documento")
    data_documento=models.DateField(verbose_name='Data emissione', db_index=True)
    @property
    def id_operazione(self):
        return self.pk
    def __unicode__(self):
        return self.fornitore.nome
    class Meta:
        db_table = u'movimentofattura'
        verbose_name_plural = "Magazzino ANTEA Entrata con bolla/fattura"
        verbose_name = "Magazzino ANTEA Entrata con bolla/fattura"
        ordering=['-data_documento']


class MovimentoFatturaDettaglio(DateUtenti):
    tipomov = models.ForeignKey(MovimentoFattura, verbose_name='Tipo di Movimento', db_index=True)
    codarticolo = models.ForeignKey(Articoli, db_index=True,verbose_name='Articolo')
    numconfezioni = models.IntegerField(null=True, db_column='numconfezioni',
                       blank=True,default=None,verbose_name='Num. Confezioni')
    numerounita = models.IntegerField(db_column='numerounita',blank=True,default=None,
                       verbose_name=u'Numero Unità')
    totalepezzi = models.IntegerField(null=True, db_column='totalepezzi',
                       default=0,verbose_name=u'Totale Unità',blank=True)
    prezzo = models.DecimalField(decimal_places=5, max_digits=14, db_column='prezzo',
              default=0.0,verbose_name='Prezzo unitario')
    sconto = models.DecimalField(decimal_places=2, max_digits=6, default=0.0,db_column='sconto')
    prezzoscontato = models.DecimalField(decimal_places=5, null=True, max_digits=14,
                      db_column='costo', blank=True,default=0.0,verbose_name='Prezzo un. scontato')
    def save(self):
        f=Articoli.objects.get(descrizione=self.codarticolo)
        ff=Articoli.objects.filter(descrizione=self.codarticolo)
#
        if self.prezzo > 0.0:
            self.prezzoscontato=self.prezzo*(1-self.sconto/100)
            if not self.numconfezioni:
                self.numconfezioni = 0
            if not self.numerounita:
                self.numerounita = 0
            self.totalepezzi = self.numconfezioni*f.quantita_conf+self.numerounita
            p=MovimentoFattura.objects.get(pk=self.tipomov_id)
            self.creato_da=p.creato_da
            self.modificato_da=p.modificato_da
            ff.update(prezzo=self.prezzo)
            ff.update(sconto=self.sconto)
            ff.update(prezzo_scontato=self.prezzoscontato)
        else:
            self.prezzo=Decimal(f.prezzo)
            self.sconto=Decimal(f.sconto)
            self.prezzoscontato=self.prezzo*(1-self.sconto/100)
            if not self.numconfezioni:
                self.numconfezioni = 0
            if not self.numerounita:
                self.numerounita = 0
            self.totalepezzi = self.numconfezioni*f.quantita_conf+self.numerounita
            p=MovimentoFattura.objects.get(pk=self.tipomov_id)
            self.creato_da=p.creato_da
            self.modificato_da=p.modificato_da
#
        super(MovimentoFatturaDettaglio,self).save()
        return
    def __unicode__(self):
        return self.codarticolo.descrizione
    class Meta:
        db_table = u'movimentofatturadettaglio'
        verbose_name_plural = "Dettaglio ANTEA entrate con bolla o fattura"
        ordering=['data_di_inserimento', ]

post_delete.connect(TotaliGiacenze, sender=MovimentoFatturaDettaglio)


class MovimentoOrdine(models.Model):
    id_ordine = models.IntegerField(primary_key=True,db_column='id_ordine', verbose_name='ordine')
    paziente = models.ForeignKey(Pazienti, db_column='paziente')
    data_emissione = models.DateField(db_column='data_emissione',verbose_name='data di emissione',
                null=False, blank=False)
    visita = models.IntegerField(db_column='visita', verbose_name='visita')
    documento = models.IntegerField(db_column='documento',blank=True,verbose_name="Num. Documento")
    consegna = models.CharField(choices=mod_consegna, max_length=10, default='R',db_column='consegna',blank=False,null=False,verbose_name=u"Modalità di consegna")
    eseguito = models.BooleanField(default=False,db_column='eseguito',null=False,blank=False)
    def __unicode__(self):
        return u"Ord.%s per %s" % (self.id_ordine, self.paziente)
    class Meta:
        db_table = u'movimentoordini'
        verbose_name_plural = "Magazzino ANTEA Ordini da cartella clinica"
        ordering=['id_ordine',]

#da riattivare dopo test
post_delete.connect(TotaliGiacenze, sender=MovimentoOrdine)
post_save.connect(TotaliGiacenze, sender=MovimentoOrdine)

class MovimentoOrdineDettaglio(models.Model):
    id_ordine = models.ForeignKey(MovimentoOrdine,db_column='id_ordine')
    codarticolo = models.ForeignKey(Articoli, db_index=True,verbose_name='Articolo',related_name='movimentoordinedettaglio_cod')
    numconfezioni = models.IntegerField(null=True, db_column='numconfezioni',
                       blank=True,default=None,verbose_name='Num. Confezioni')
    numerounita = models.IntegerField(db_column='numerounita',blank=True,default=None,
                       verbose_name=u'Numero Unità')
    totalepezzi = models.IntegerField(null=True, db_column='totalepezzi',
                       default=0,verbose_name=u'Totale Unità',blank=True)
    fatto = models.BooleanField(default=False,db_column='fatto')
    @property
    def collocazione(self):
        for m in magazzino:
            if m[0] == self.codarticolo.idmagazzino:
                break
        pos = (m[1] + ':' + posizione[self.codarticolo.colarm-1][1] + '-' + posizione[self.codarticolo.piano-1][1] + '-' + posizione[self.codarticolo.altrorif1-1][1])
        return pos
    def save(self):
        f=Articoli.objects.get(descrizione=self.codarticolo)
        if not self.numconfezioni:
            self.numconfezioni = 0
        if not self.numerounita:
            self.numerounita = 0
        self.totalepezzi = self.numconfezioni*f.quantita_conf+self.numerounita
        super(MovimentoOrdineDettaglio,self).save()
# Se TUTTI gli articoli dell'ordine hanno fatto=True imposta anche l'ordine eseguito
        s = MovimentoOrdineDettaglio.objects.filter(id_ordine=self.id_ordine)
        z = MovimentoOrdineDettaglio.objects.filter(id_ordine=self.id_ordine,fatto=True)
        w = MovimentoOrdine.objects.get(id_ordine=s[0].id_ordine_id)
        if s.count() == z.count():
            w.eseguito = True
        else:
            w.eseguito = False
        w.save()
        return
    class Meta:
        db_table = u'movimentoordinedettaglio'
        verbose_name_plural = "Magazzino ANTEA Dettaglio Ordini da Cart.Cl."

post_delete.connect(TotaliGiacenze, sender=MovimentoOrdineDettaglio)


class ArticoliNonMagazzino(models.Model):
    id_ordine = models.ForeignKey(MovimentoOrdine,db_column='id_ordine')
    codice_AIFA = models.CharField(max_length=12, db_index=True,verbose_name='Codice AIFA')
    codice = models.CharField(max_length=15, db_index=True,verbose_name='Codice Magazzino')
    descrizione = models.CharField(max_length=70,db_index=True,verbose_name='Descrizione')
    confezioni = models.IntegerField(db_column='confezioni',blank=True,default=None,verbose_name=u'Num. confezioni')
    crea = models.BooleanField(default=False, db_column="crea")
    class Meta:
        db_table = u'articolinonmagazzino'
        verbose_name_plural = "Magazzino ANTEA Ordini da Cart.Cl. ** NON IN MAGAZZINO **"


class FarmaciAIFA(models.Model):
    id_aifa = models.CharField(primary_key=True,max_length=20,db_column='id_aifa', verbose_name='Cod. AIFA')
    cod_magazzino = models.CharField(max_length=20,db_column='cod_magazzino', verbose_name='Cod. Magazzino',blank=True,null=True,db_index=True)
    nome_farmaco = models.CharField(max_length=100,db_column='nome_farmaco', verbose_name='Nome Farmaco',blank=False,null=False,db_index=True)
    crea_farmaco = models.BooleanField(default=False, db_column="crea_farmaco",verbose_name='Crea farmaco in articoli')
    creato = models.BooleanField(default=False, db_column="creato")
    def save(self):
        if self.crea_farmaco:
            try:
                q = Articoli.objects.get(codice=self.cod_magazzino)
                if q.descrizione != self.nome_farmaco:
                    q.update(descrizione = self.nome_farmaco)
                q.update(codice_articolo_fornitore=self.id_aifa)
            except:
                q = Articoli(codice=self.cod_magazzino,
                            descrizione=self.nome_farmaco,
                            codice_articolo_fornitore=self.id_aifa)
                q.save()
                self.creato=True
        return super(FarmaciAIFA,self).save()
    def __unicode__(self):
        return u"%s" % (self.nome_farmaco)
    class Meta:
        db_table = u'farmaci_aifa'
        verbose_name_plural = "Farmaci AIFA"
        ordering=['nome_farmaco','id_aifa']

class Kit_Antea(models.Model):
    codarticolo = models.ForeignKey(Articoli, db_index=True,verbose_name='Articolo')
    numconfezioni = models.IntegerField(null=True, db_column='numconfezioni',
                       default=0,verbose_name='Num. Confezioni')
    numerounita = models.IntegerField(db_column='numerounita',default=0,
                       verbose_name=u'Numero Unità')
    totalepezzi = models.IntegerField(db_column='totalepezzi',
                       default=0,verbose_name=u'Totale Unità')
    def save(self):
        f=Articoli.objects.get(descrizione=self.codarticolo)
        if not self.numconfezioni:
            self.numconfezioni = 0
        if not self.numerounita:
            self.numerounita = 0
        self.totalepezzi = self.numconfezioni*f.quantita_conf+self.numerounita
        super(Kit_Antea,self).save()
        return
    class Meta:
        db_table = u'kit_antea'
        verbose_name_plural = "Kit di base ANTEA"

class Principi_Attivi(models.Model):
    idpa = models.CharField(primary_key=True,max_length=6,db_column='idpa')
    descrizione = models.CharField(max_length=200, db_column='descrizione', db_index=True, unique=False)
    codice = models.CharField(max_length=70, db_column='codice', db_index=True, unique=False)
    altro_id = models.CharField(max_length=15, db_column='altro_id', db_index=True, unique=False)
    def __unicode__(self):
        return u"%s: %s" % (self.descrizione, self.codice)
    class Meta:
        db_table = u'principi_attivi'
        verbose_name_plural = "Principi Attivi"
        ordering=['descrizione','codice']

class Forma_Farmaceutica(models.Model):
    cod = models.CharField(primary_key=True,max_length=2,db_column='cod')
    descrizione = models.CharField(max_length=50, db_column='descrizione', db_index=True, unique=False)
    def __unicode__(self):
        return u"%s: %s" % (self.descrizione, self.cod)
    class Meta:
        db_table = u'forma_farmaceutica'
        verbose_name_plural = "Forma Farmaceutica"
        ordering=['descrizione','cod']


class Tutti_Articoli(models.Model):
    descrizione = models.CharField(max_length=40, db_column='descrizione', db_index=True, unique=False)
    cod_aifa = models.CharField(primary_key=True,max_length=9,db_column='cod_aifa')
    cod_mag = models.CharField(max_length=6, db_column='cod_mag', db_index=True, unique=True)
    principio_attivo = models.ForeignKey(Principi_Attivi, verbose_name='Principio Attivo',db_column='idpa')
    forma = models.ForeignKey(Forma_Farmaceutica, verbose_name='Forma Farmaceutica',db_column='formafarmaceutica')
    quant_num = models.IntegerField(db_column='quant_num',blank=True,null=True,default=None,verbose_name=u'Quantità num')
    quant_lett = models.IntegerField(db_column='quant_lett',blank=True,null=True,default=None,verbose_name=u'Quantità lett')
    dec_quant = models.IntegerField(db_column='dec_quant',blank=True,default=2,verbose_name=u'Decimali Quantità')
    dec_dos = models.IntegerField(db_column='dec_dos',blank=True,default=2,verbose_name=u'Decimali Dosaggio')
    vds =  models.CharField(max_length=2, db_column='vds')
    prezzo = models.DecimalField(decimal_places=3, max_digits=10, db_column='prezzo',default=0.0,verbose_name='Prezzo (Euro)')
    presente = models.BooleanField(default=False, db_column="presente")
    def save(self):
        self.cod_mag = decode32(self.cod_aifa)
        super(Tutti_Articoli,self).save()
    def __unicode__(self):
        return u"%s" % (self.descrizione)
    class Meta:
        db_table = u'tutti_articoli'
        verbose_name_plural = "Tutti gli articoli"
        ordering=['descrizione','cod_mag']
