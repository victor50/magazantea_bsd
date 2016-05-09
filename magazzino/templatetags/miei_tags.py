from django import template
register = template.Library()

@register.filter(name='visualizza_model')
def visualizza_model(value):
    lista_no = ["Articoli Lista", "Dettaglio Movimenti senza bolla o fattura", \
        "Dettaglio entrate con bolla o fattura"]
    if str(value) not in lista_no:
        return 1
    else:
        return 0
