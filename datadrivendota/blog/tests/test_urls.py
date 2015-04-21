from django.test import TestCase, Client
from model_mommy import mommy
from blog.models import Entry


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(self):
        self.entry = mommy.make_recipe('blog.entry', publicity=Entry.PUBLIC)
        super(TestUrlconf, self).setUpClass()

    def test_url_200(self):
        c = Client()

        resp = c.get('/blog/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/blog/entry/{0}/'.format(self.entry.id))
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/blog/rss/')
        self.assertEqual(resp.status_code, 200)

    @classmethod
    def tearDownClass(self):
        self.entry.delete()
        super(TestUrlconf, self).setUpClass()
