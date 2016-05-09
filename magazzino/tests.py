"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
"""
###### aggiunto da me
import os

# Set the DJANGO_SETTINGS_MODULE environment variable.
os.environ['DJANGO_SETTINGS_MODULE'] = "antea.settings"

###### fine aggiunto da me
"""
from django.test import TestCase



class MagazanteaViewsTestCase(TestCase):
    def test_index(self):
        resp = self.client.get('/magazzino/')
#        print('%s') %(resp)
        self.assertEqual(resp.status_code, 200)
        resp = self.client.get('/magazzino/listarticoli/')
#        print('%s') %(resp)
        self.assertEqual(resp.status_code, 200)

