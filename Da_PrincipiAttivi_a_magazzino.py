#-*- coding: utf-8 -*-
# Dal file filpa.txt dei principi attivi ottenuto da > utilità > esporta del prog
# Farmadata importo nella tabella di magazzino principi_attivi
# (PrincipiAttivi.txt = filpa.txt)

inp=open("PrincipiAttivi.txt","r")
from magazzino.models import Principi_Attivi as pa
for line in inp:
    rec = pa(idpa=line[3:9],descrizione=line[9:209],codice=line[209:279],altro_id=line[279:294])
    rec.save()