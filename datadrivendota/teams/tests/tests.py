from django.templatetags.static import static
from django.test import TestCase, Client
from model_mommy import mommy
from django.utils import timezone
from datetime import timedelta
from utils.file_management import fake_image


class TestModelMethods(TestCase):

    def setUp(self):
        self.team = mommy.make_recipe('teams.team')

    def test_update_save(self):
        self.team.save()
        self.assertLess(
            timezone.now() - self.team.update_time,
            timedelta(seconds=.1)
        )

    def test_outdated(self):
        self.team.update_time = timezone.now() - timedelta(weeks=10)
        self.team.stored_image = None
        self.assertEqual(self.team.is_outdated, True)

        self.team = fake_image(self.team)
        self.team.update_time = timezone.now() - timedelta(weeks=10)
        self.assertEqual(self.team.is_outdated, False)

        self.team.update_time = timezone.now()
        self.team.stored_image = None
        self.assertEqual(self.team.is_outdated, False)

        self.team = fake_image(self.team)
        self.team.update_time = timezone.now()
        self.assertEqual(self.team.is_outdated, False)


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.team = mommy.make_recipe('teams.team')

    def test_url_ok(self):
        c = Client()

        resp = c.get('/teams/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/teams/{0}/'.format(self.team.steam_id))
        self.assertEqual(resp.status_code, 200)

        # The -1 represents a team that does not exist,
        # because steam ids are positive.
        resp = c.get('/teams/{0}/'.format(-1))
        self.assertEqual(resp.status_code, 404)

    def test_image(self):

        t = mommy.make('teams.team', stored_image=None)
        self.assertEqual(t.image, static('blank_team.png'))
        t.delete()

        t = mommy.make('teams.team')
        t = fake_image(t)

        self.assertNotEqual(t.image, static('blank_team.png'))
        t.delete()
