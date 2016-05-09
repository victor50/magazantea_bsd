#-*- coding: utf-8 -*-
# Dal file testo delle forme farmaceuticheottenuto da > utilità > esporta del prog
# Farmadata importo nella tabella di magazzino Forma_Farmaceutica
# (PrincipiAttivi.txt = filpa.txt)

inp=open("FormaFarmaceutica.txt","r")
from magazzino.models import Forma_Farmaceutica as fm
for line in inp:
    rec = fm(cod=line[0:2],descrizione=line[3:53])
    rec.save()