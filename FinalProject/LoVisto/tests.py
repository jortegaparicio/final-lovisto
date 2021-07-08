from django.test import TestCase, Client

# Create your tests here.

from django.test import TestCase
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

class PostTests(TestCase):

    def test_login(self):
        user_name = 'usuario'
        password = 'user'
        login = 'login'
        c = Client()
        response = c.post('/LoVisto/', {'action': login,'username': user_name, 'password': password})
        self.assertEqual(response.status_code, 200)
        response = c.get('/LoVisto/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)

    def test_logout(self):
        logout = 'logout'
        c = Client()
        response = c.post('/LoVisto/allcontent', {'action': logout})
        self.assertEqual(response.status_code, 200)
        response = c.get('/LoVisto/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)

    def test_changeMode(self):
        action = 'changeMode'
        c = Client()
        response = c.post('/LoVisto/1', {'action': action})
        self.assertEqual(response.status_code, 200)
        response = c.get('/LoVisto/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)


    def test_login2(self):
        user_name = 'usuario'
        password = 'user'
        login = 'login'
        c = Client()
        response = c.post('/LoVisto/information', {'action': login,'username': user_name, 'password': password})
        self.assertEqual(response.status_code, 200)
        response = c.get('/LoVisto/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)


    def test_changeMode2(self):
        action = 'changeMode'
        c = Client()
        response = c.post('/LoVisto/user', {'action': action})
        self.assertEqual(response.status_code, 200)
        response = c.get('/LoVisto/')
        self.assertEqual(response.status_code, 200)
        content = response.content.decode('utf-8')
        self.assertIn('<h2>Menú</h2>', content)