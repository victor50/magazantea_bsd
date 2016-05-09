from barpy import GS1128, Code128, Code128A, EAN13, QrCode, HtmlOutputter
#
from magazantea.settings import MEDIA_ROOT
#
def CreaCodiceBarra(stringa,file_img):
    stringa = stringa.strip().replace(" ", "_").replace("/","_").replace(".","_")
    code = Code128(stringa,'B')
    outputter = code.outputter_for("to_png")
    nomefile = MEDIA_ROOT + file_img
    f = open(nomefile,"w")
    f.write(outputter.to_png(margin=5, height=100, width=800, xdim=2, ydim=2))
    f.close()
    return
