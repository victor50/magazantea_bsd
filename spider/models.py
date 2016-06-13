#-*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import pre_delete,post_delete,post_save,pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.cache import cache
from django_cache_manager.cache_manager import CacheManager
from magazzino.models import *
from comune.signals import *
from comune.prog_servizio import *
from magazantea.settings import MEDIA_ROOT



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

class OrdineSpider(models.Model):
    paziente = models.ForeignKey(Pazienti, db_column='paziente')
    data_emissione = models.DateTimeField(db_column='data_emissione',verbose_name='data di emissione',
                null=False, blank=False)
    operatore = models.ForeignKey(Operatori, db_column='operatore', to_field='id_spider')
    consegna = models.CharField(choices=mod_consegna, max_length=10, default='R',db_column='consegna',blank=False,null=False,verbose_name=u"Modalità di consegna")
    eseguito = models.BooleanField(default=False,db_column='eseguito',null=False,blank=False)
    def __unicode__(self):
        return u"Ord.%s per %s" % (self.pk, self.paziente)
    class Meta:
        db_table = u'ordinespider'
        verbose_name_plural = "Magazzino ANTEA Ordini da Spider"
        ordering=['data_emissione','pk']

post_save.connect(TotaliGiacenze, sender=OrdineSpider)
post_delete.connect(TotaliGiacenze, sender=OrdineSpider)

class OrdineSpiderDettaglio(models.Model):
    id_ordine = models.ForeignKey(OrdineSpider,db_column='id_ordine')
    codarticolo = models.ForeignKey(Articoli, db_index=True,verbose_name='Articolo',related_name='ordinespiderdettaglio_cod')
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
        super(OrdineSpiderDettaglio,self).save()
# Se TUTTI gli articoli dell'ordine hanno fatto=True imposta anche l'ordine eseguito
        s = OrdineSpiderDettaglio.objects.filter(id_ordine=self.id_ordine)
        z = OrdineSpiderDettaglio.objects.filter(id_ordine=self.id_ordine,fatto=True)
        w = OrdineSpider.objects.get(id=s[0].id_ordine_id)
        if s.count() == z.count():
            w.eseguito = True
        else:
            w.eseguito = False
        w.save()
        return
    class Meta:
        db_table = u'ordinespiderdettaglio'
        verbose_name_plural = "Magazzino ANTEA Dettaglio Ordini da Spider"

post_delete.connect(TotaliGiacenze, sender=OrdineSpiderDettaglio)

class ArticoliSpiderNonMagazzino(models.Model):
    id_ordine = models.ForeignKey(OrdineSpider,db_column='id_ordine')
    descrizione = models.CharField(max_length=70,db_index=True,verbose_name='Descrizione')
    numconfezioni = models.IntegerField(db_column='numconfezioni',blank=True,default=None,verbose_name=u'Num. confezioni')
    crea = models.BooleanField(default=False, db_column="crea")
    class Meta:
        db_table = u'articolispidernonmagazzino'
        verbose_name_plural = "Magazzino ANTEA Ordini da Spider ** NON IN MAGAZZINO **"
