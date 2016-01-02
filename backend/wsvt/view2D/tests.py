from django.core.urlresolver import resolve
from django.test import TestCase
from view2D.views import *

class IndexTest(TestCase):
    def test_URLResolvesToIndexView(self):
        found = resolve('/view2D')
        self.assertEqual(found.func, index)

# TODO add other test