from django.db import connections
class DBRouter(object):
    """A router to control all database operations on models in
        the contrib.auth application"""
    def db_for_read(self, model,**hints):
        if hasattr(model,'nome_db'):
            return model.nome_db
        return None
    def db_for_write(self, model,**hints):
        if hasattr(model,'nome_db'):
            return model.nome_db
        return None
    def allow_syncdb(self, db, model):
        if hasattr(model,'nome_db'):
            return model.nome_db == db
        return db =='default'

