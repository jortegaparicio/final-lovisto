from django.test import TestCase, Client

# Create your tests here.

from django.test import TestCase
from . import aemet_parser
from . import redditParser
from . import YTparser
from django.test import Client

class GetTests(TestCase):
    def test_index(self):
        c = Client()
        response = c.get('/LoVisto/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)

    def test_allcontent(self):
        c = Client()
        response = c.get('/LoVisto/allcontent')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)

    def test_content(self):
        c = Client()
        response = c.get('/LoVisto/1')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<a href="/login">Authentication here</a>', content)

    def test_information(self):
        c = Client()
        response = c.get('/LoVisto/information')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)

    def test_user(self):
        c = Client()
        response = c.get('/LoVisto/user')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<p align="center">THIS WEBSITE IS ABLE ONLY FOR AUTHENTICATED USERS</p>', content)




