from django.test import TestCase


class SimpleItemUrlTest(TestCase):
    fixtures = ['test_fixture.json']

    def test_urls(self):
        urls = ['', 'winrate/']
        for url in urls:
            strng = "/items/"+url
            resp = self.client.get(strng)
            self.assertEqual(resp.status_code, 200)
