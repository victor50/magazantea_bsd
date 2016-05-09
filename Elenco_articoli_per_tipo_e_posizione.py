from magazzino.models import Articoli
from django.utils.encoding import smart_str

out_file = open("elenco.txt","w")

categorie_abbreviazioni = ((1, 'Farmaci','FA'), (2, 'Dispositivi sanitari','DS'),\
     (3, 'Generale','GE'),  (4, 'Materiale di consumo','MC'), (5, 'Medicazioni','ME'),)

categoria = [(cat[0],cat[1]) for cat in categorie_abbreviazioni]

cat={}
for c in categoria:
    cat[c[0]]=c[1]


magazzino = ((10,'1'),(20,'2'),(30,'3'),(40,'CARRELLO EMERGENZA'),(50,'FRIGORIFERO'), \
             (60,'HOSPICE'),(70,'MEDICHERIA'),)
mag={}
for m in magazzino:
    mag[m[0]]=m[1]

posizione = ((1,''),  (2, '01'),  (3, '02'),  (4, '03'),  (5, '04'),  (6, '05'), \
  (7, '06'),  (8, '07'),  (9, '08'),  (10, '09'),  (11, '10'),  \
  (12, '11'),  (13, '12'),  (14, '13'),  (15, '14'),  (16, '15'),  \
  (17, '16'),  (18, '17'),  (19, '18'),  (20, '19'),  (21, '20'),  \
  (22, 'A'),  (23, 'B'),  (24, 'C'),  (25, 'D'),  (26, 'E'),  \
  (27, 'F'),  (28, 'G'),  (29, 'H'),  (30, 'I'),  (31, 'J'),  \
  (32, 'K'),  (33, 'L'),  (34, 'M'),  (35, 'N'),  (36, 'O'),  \
  (37, 'P'),  (38, 'Q'),  (39, 'R'),  (40, 'S'),  (41, 'U'),  \
  (42, 'V'),  (43, 'W'),  (44, 'X'),  (45, 'Y'),  (46, 'Z'),)

pos={}
for p in posizione:
    pos[p[0]]=p[1]

out_file.write("Categoria;Codice;Descrizione;Magazzino;Stanza;Colonna;Ripiano\n")
art=Articoli.objects.all().order_by('categoria','descrizione')
for q in art:
    stringa='%s;%s;%s;%s;%s;%s;%s;%s' %(cat[q.categoria],'="'+q.codice+'"',q.descrizione,mag[q.idmagazzino],pos[q.colarm], pos[q.piano], pos[q.altrorif1], pos[q.altrorif2]+'\n')
    out_file.write(smart_str(stringa))
out_file.close()