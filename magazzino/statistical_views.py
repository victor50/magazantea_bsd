#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django import forms
from magazzino.models import *

class IntervalloDateForm(forms.Form):
    # the default format is %Y-%m-%d
    data_iniziale = forms.DateField(label='Data Inizio Analisi (AAAA-MM-GG)',widget=forms.widgets.DateInput(format="%d/%m/%Y"), required=False)
    data_finale = forms.DateField(label='Data Fine Analisi (AAAA-MM-GG)',widget=forms.widgets.DateInput(format="%d/%m/%Y"), required=False)
    def cleaned_data_finale(self):
        if (self.cleaned_data['data_finale'] < self.cleaned_data['data_iniziale']):
            raise forms.ValidationError("La data iniziale deve essere precedente alla data finale")
        return self.cleaned_data['data_finale']


@login_required
def costi_per_paziente(request):
    import os
    ris = None
# Inizializza una pagina vuota web in statcosti.html
    my_command = '/usr/local/bin/Rscript /usr/local/www/magazantea/r-base/inizializza.R'
    print my_command
    os.system(my_command)
# Fine inizializzazione
    if request.method == 'POST':
        form = IntervalloDateForm(request.POST)
        if form.is_valid():
            data_in = form.cleaned_data['data_iniziale']
            data_fi = form.cleaned_data['data_finale']
            if data_fi < data_in:
                raise forms.ValidationError("La data iniziale deve essere precedente alla data finale")
            print data_in,data_fi
            my_command = '/usr/local/bin/Rscript /usr/local/www/magazantea/r-base/costi_per_paziente.R "' + str(form.cleaned_data['data_iniziale']) + '" "' + str(form.cleaned_data['data_finale']) + '"'
            print my_command
            ris = os.system(my_command)
            print 'ris ='
            print ris
    else:
        form = IntervalloDateForm()
#    my_command = '/usr/local/bin/Rscript /home/victor/r-base/costi_per_paziente.R "' + str(data_in) + '" "' + str(data_fi) + '"'
#    print my_command
 #   ris = os.command(my_command)
#    ris = 0
    return render_to_response('stat_costoxpaziente.html',
        {'form':form,'ris':ris}, RequestContext(request))
#     context = {'risultati': risultati}
#     return render(request, 'stat_costoxpaziente.html', context)