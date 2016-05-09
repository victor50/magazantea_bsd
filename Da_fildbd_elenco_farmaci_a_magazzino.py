#-*- coding: utf-8 -*-
# Dal file enorme filbd.txt dei farmaci ottenuto da > utilità > esporta del prog
# Farmadata importo nella tabella di magazzino articoli_tutti
# (PrincipiAttivi.txt = filpa.txt)

inp=open("filbd.txt","r")
from magazzino.models import Forma_Farmaceutica as fm
for line in inp:
    rec = pa(idpa=line[3:9],descrizione=line[9:209],codice=line[209:279],altro_id=line[279:294])
    rec.save()