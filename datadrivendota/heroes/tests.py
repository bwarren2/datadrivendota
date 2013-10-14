"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from io import StringIO
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.core.files import File
from django.utils.text import slugify
from .models import Hero

class HeroViewsTest(TestCase):

    def setUp(self):
        User.objects.create_user('temporary', 'temporary@gmail.com', 'temporary')
        s = slugify(u'Juggernaut')
        self.hero = Hero.objects.create(name='Juggernaut',
            steam_id=8,machine_name=s)
        openfile = StringIO()
        openfile.write(u'test')
        self.hero.thumbshot.save('a',File(openfile))
        self.hero.mugshot.save('a',File(openfile))

    def test_valid_urls(self):
        """
        Check that the URLs we expect to resolve do.
        """
        c = Client()
        c.login(username='temporary',password='temporary')
        resp = self.client.get('/heroes')
        self.assertEqual(resp.status_code,200)
        resp = self.client.get('/heroes/vitals')
        self.assertEqual(resp.status_code,200)
        resp = self.client.get('/heroes/lineups')
        self.assertEqual(resp.status_code,200)
        resp = self.client.get('/heroes/performance/')
        self.assertEqual(resp.status_code,200)
        resp = self.client.get('/heroes/skill_bars/')
        self.assertEqual(resp.status_code,200)
        url = '/heroes/'+self.hero.machine_name
        resp = c.get(url)
        self.assertEqual(resp.status_code,200)
