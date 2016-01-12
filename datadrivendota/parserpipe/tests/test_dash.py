from django.test import TestCase, Client
from django.core.urlresolvers import reverse


class TestParserDash(TestCase):

    def test_staff_required(self):

        c = Client()
        resp = c.get(reverse("parserpipe:dash"))
        self.assertRedirects(
            resp,
            '/admin/login/?next=/parser-management/'
        )

        resp = c.get(reverse("parserpipe:tasks"))
        self.assertEqual(resp.status_code, 405)
