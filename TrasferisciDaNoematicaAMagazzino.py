#-*- coding: utf-8 -*-
#Vai sotto la directory del progetto
import os
os.chdir('/home/victor/magazantea')

# Chiama django per l'esecuzione in uno script python
# equivale al comando "manage.py shell"
os.environ.setdefault('DJANGO_SETTINGS_MODULE','magazantea.settings')
import magazantea.settings
#######

import datetime
#Chiama le tabelle fornite da noematica
from noematica.models import ordini_magazzino as ordini_noe,magazzino_specifica_ordini as specifica_noe, magazzino_conferma_ordini as conferma_noe
#Chiama le tabelle da alimentare con i dati di noematica in magazzino
from magazzino.models import ArticoliLista, Pazienti as pazienti_mg,MovimentoOrdine as ordine_mg, MovimentoOrdineDettaglio as specifica_mg
from comune.signals import EseguiQuery
# Carica nel queryset tutti i record della tabella pazienti-ordini di noematica
ord = ordini_noe.objects.all()
oggi = datetime.date.today()
#
#Carica o modifica in magazzino i pazienti con loop dei record
#di ord  previa verifica di condizioni
for q in ord:
# Verifica se il paziente non esiste
    if not pazienti_mg.objects.filter(id = q.id_pat_hosp):
        # Carica il record paziente
        p = pazienti_mg(id=q.id_pat_hosp, cognome=q.surname, nome=q.name,
                cf=q.fiscal_code, datanascita=q.birth_date, luogo=q.birth_place,
                indirizzo=q.street, citta=q.city, cap=q.zip_code, telefoni=q.phone,
                cessato=q.deceduto)
        p.save()
#Se il paziente esiste
    else:
    #Verifica che non sia cessato altrimenti flagga
        p = pazienti_mg.objects.get(id = q.id_pat_hosp)
        if  p.cessato != q.deceduto:
            p.cessato = q.deceduto
            if q.deceduto:
                p.data_chiusura = oggi
            else:
                p.data_chiusura = None
            p.save()
    #
    # Verifica che tutti i campi del paziente siano uguali in noematica ed in magazzino
    # se no, correggi
        if  p.cf != q.fiscal_code:
            p.cf = q.fiscal_code
            p.save()
        if  p.datanascita != q.birth_date:
            p.datanascita = q.birth_date
            p.save()
        if  p.luogo != q.birth_place:
            p.luogo = q.birth_place
            p.save()
        if  p.indirizzo != q.street:
            p.indirizzo = q.street
            p.save()
        if  p.citta != q.city:
            p.citta = q.city
            p.save()
        if  p.datanascita != q.birth_date:
            p.datanascita = q.birth_date
            p.save()
        if  p.cap != q.zip_code:
            p.cap = q.zip_code
            p.save()
        if  p.telefoni != q.phone:
            p.telefoni = q.phone
            p.save()
#
# Carica il nuovo ordine, se non c'è, in ordine_mg (MovimentoOrdine di magazzino)
    if not ordine_mg.objects.filter(id_ordine = q.id_ordine):
        p = pazienti_mg.objects.get(id = q.id_pat_hosp)
        r = ordine_mg(id_ordine=q.id_ordine, paziente =p,
                data_emissione=q.commission_date, riferimento_antea=q.commission_user)
        r.save()
#
    # Dichiara letto il record di ord
        q.readed = True
        q.save()

det = specifica_noe.objects.all()
#
for d in det:
    art = ArticoliLista.objects.get(codice=d.cod_magazzino_ext)
    ord = ordine_mg.objects.get(id_ordine=d.id_ordine_id)
    if not specifica_mg.objects.filter(id_ordine=d.id_ordine_id, codarticolo=d.cod_magazzino_ext):
        print("Order %s for article %s does not exist-load now") % (d.id_ordine_id,d.cod_magazzino_ext)
        rec = specifica_mg(id_ordine=ord, codarticolo=art,numerounita=d.qta, fatto=0)
        rec.save()
#
#



