from functools import wraps

import factory

from django.contrib.auth.models import User, Permission
from django.test import TestCase

from players.models import Player


## Test Factories
class UserFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = User

    username = factory.Sequence(lambda n: 'person{0}'.format(n))
    email = factory.Sequence(lambda n: 'person{0}@example.com'.format(n))
    first_name = "Test"
    last_name = "User"

    @factory.post_generation
    def password(self, create, extracted, **kwargs):
        self.set_password(self.username)


class PlayerFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Player

    steam_id = factory.Sequence(lambda n: n + 1)
    persona_name = factory.Sequence(lambda n: 'Steam{0}'.format(n))
    updated = True


### Test Utils

class LoginError(Exception):
    pass


def logged_in(user_factory):
    def logged_in(f):
        @wraps(f)
        def wrapper(self, *args, **kwargs):
            user = user_factory.create()
            username = user.username
            password = user.username
            permissions = Permission.objects.filter(
                codename__in=['can_look', 'can_touch']
            )
            user.user_permissions = permissions
            user.save()
            if not self.client.login(username=username, password=password):
                raise LoginError
            return f(self, user, *args, **kwargs)
        return wrapper
    return logged_in


# Tests

class IntegrationTest(TestCase):
    pass


class CoreIntegrationTest(IntegrationTest):
    def test_redirect_to_login(self):
        r = self.client.get('/')
        self.assertEqual(r.status_code, 302)
        # Is this the best way to check headers?
        self.assertIn(
            "http://testserver/login/?next=/",
            r._headers['location']
        )


class HeroesIntegrationTest(IntegrationTest):
    @logged_in(UserFactory)
    def test_index(self, user):
        r = self.client.get('/heroes/')
        self.assertEqual(r.status_code, 200)

    # def test_vitals_get(self):
    #     self.get('/heroes/vitals/')
    #     self.assertEqual(self.css_count("#id_heroes"), 1)
    #     self.assertEqual(self.css_count("input[name=stats]"), 7)
    #     self.assertEqual(self.css_count("input[name=unlinked_scales]"), 1)

    # def test_vitals_post(self):
    #     self.get('/heroes/vitals/')
    #     # The following form entry fails because the database is not
    #     # initialized correctly.
    #     self.css_single('#id_heroes').send_keys("Faceless Void")
    #     self.css_single('#id_stats_3').click()
    #     self.css_single('#id_stats_5').click()
    #     self.css_single('button[type=submit]').click()
    #     self.assertEqual(self.css_count('.error'), 0)

    # def test_vitals_post_bad(self):
    #     self.get('/heroes/vitals/')
    #     # The following form entry fails because the database is not
    #     # initialized correctly.
    #     self.css_single('#id_heroes').send_keys("This hero doesn't exist")
    #     self.css_single('#id_stats_3').click()
    #     self.css_single('#id_stats_5').click()
    #     self.css_single('button[type=submit]').click()
    #     self.assertEqual(self.css_count('.error'), 1)

# Heroes
#  (Possibly slow-ajax-images on some pages, check)
#  Vitals
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Lineups
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Performance
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Skillbars
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)

# Items
#  Index
#  Instance

# Matches
#  Index
#  Instance (test for ajax-grabbed slow image)

# Players
#  Detail
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Winrate
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Timeline
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Matches
#   Generates a table
