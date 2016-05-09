    list_per_page = 500
    readonly_fields = ['creato_da','modificato_da','data_di_inserimento','data_di_modifica']
    list_filter=['creato_da','data_di_inserimento','modificato_da','data_di_modifica']

    def save_formset(self, request, form, formset, change):
        obj = formset.save()
        utente = unicode(request.user)
        print("Utente %s, Obj= %s" % (utente,dir(obj))
#        if change:
#            obj.modificato_da = utente
 #       else:
#            obj.creato_da = utente
 #       obj.save()

    def save_formset(self, request, form, formset, change):
        formset.save()
        utente = unicode(request.user)
        for f in formset.forms:
            obj=f.instance
            if change:
                print("Modificato da %s, Obj= %s" % (utente,dir(obj))
                obj.modificato_da = utente
            else:
                print("Creato da %s, Obj= %s" % (utente,dir(obj))
                obj.creato_da = utente
            obj.save()
