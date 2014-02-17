"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""
from django.contrib.auth.models import User
from django.test.client import Client
from django.test import TestCase
from django.core.urlresolvers import reverse
from .r import (
    HeroPerformanceChart,
    HeroSkillLevelBwChart,
    generateChart,
    lineupChart
)
from matches.tests import MatchValidityMixin
from .test_mixins import HeroValidityMixin


# TESTS
# R
# @todo: Consider using factoryboy for generating test objects. It's a cool
# library!
# --kit 2014-02-16
class HeroVitalsTestCase(HeroValidityMixin, TestCase):
    fixtures = ['datadrivendota/heroes/test_data.json']

    def setUp(self):
        User.objects.create_user(
            'temporary',
            'temporary@gmail.com',
            'temporary'
        )
        super(HeroVitalsTestCase, self).setUp()

    def test_invalid_hero(self):
        foo = generateChart(
            hero_list=[self.invalid_hero],
            stats_list=[self.valid_stat],
            display_options={'linked_scales': "relation='free'"}
        )
        self.assertEqual(foo.name, u'failface.png')

    def test_invalid_stat(self):
        foo = generateChart(
            hero_list=[self.valid_hero],
            stats_list=[self.invalid_stat],
            display_options={'linked_scales': "relation='free'"}
        )
        self.assertEqual(foo.name, u'failface.png')

    def test_valid_call(self):
        foo = generateChart(
            hero_list=[self.valid_hero],
            stats_list=[self.valid_stat],
            display_options={'linked_scales': "relation='free'"}
        )
        self.assertNotEqual(foo.name, u'failface.png')

    def test_valid_post(self):
        c = Client()
        c.login(username='temporary', password='temporary')
        # @todo: Come come, camel case is not very Pythonic! We prefer
        # underscores.
        # --kit 2014-02-16
        postOpts = {
            'heroes': self.test_hero.name,
            'stats': self.valid_stat,
            'unlinked_scales': True
        }
        resp = self.client.post(reverse("heroes:vitals"), postOpts)
        self.assertNotEqual(resp.context['imagebase'], u'failface.png')


class HeroLineupTestCase(HeroValidityMixin, TestCase):
    fixtures = ['datadrivendota/heroes/test_data.json']

    def setUp(self):
        User.objects.create_user(
            'temporary',
            'temporary@gmail.com',
            'temporary'
        )
        super(HeroLineupTestCase, self).setUp()

    def test_invalid_hero(self):
        foo = lineupChart(
            heroes=[self.invalid_hero],
            stat=self.valid_stat,
            level=self.valid_level
        )
        self.assertNotEqual(foo.name, 'failface.png')
        # Because lineup hero is only optional for coloration

    def test_invalid_stat(self):
        foo = lineupChart(
            heroes=[self.valid_hero],
            stat=self.invalid_stat,
            level=self.valid_level
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_level(self):
        foo = lineupChart(
            heroes=[self.valid_hero],
            stat=self.valid_stat,
            level=self.invalid_level
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_valid_call(self):
        foo = lineupChart(
            heroes=[self.valid_hero],
            stat=self.valid_stat,
            level=self.valid_level
        )
        self.assertNotEqual(foo.name, 'failface.png')

    def test_valid_post(self):
        c = Client()
        c.login(username='temporary', password='temporary')
        postOpts = {
            'heroes': self.test_hero.name,
            'stats': self.valid_stat,
            'level': self.valid_level
        }
        resp = self.client.post(reverse("heroes:lineup"), postOpts)
        self.assertNotEqual(resp.context['imagebase'], 'failface.png')


class HeroPerformanceTestCase(HeroValidityMixin, MatchValidityMixin, TestCase):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        User.objects.create_user(
            'temporary',
            'temporary@gmail.com',
            'temporary'
        )
        super(HeroPerformanceTestCase, self).setUp()

    def test_invalid_hero(self):
        foo = HeroPerformanceChart(
            hero=self.invalid_hero,
            game_mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            group_var=self.valid_cat_var,
            split_var=self.valid_cat_var,
            player=None
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_game_modes(self):
        foo = HeroPerformanceChart(
            hero=self.valid_hero,
            game_mode_list=self.invalid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            group_var=self.valid_cat_var,
            split_var=self.valid_cat_var,
            player=None
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_x_var(self):
        foo = HeroPerformanceChart(
            hero=self.valid_hero,
            game_mode_list=self.valid_game_modes,
            x_var=self.invalid_x_var,
            y_var=self.valid_y_var,
            group_var=self.valid_cat_var,
            split_var=self.valid_cat_var,
            player=None
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_y_var(self):
        foo = HeroPerformanceChart(
            hero=self.valid_hero,
            game_mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.invalid_y_var,
            group_var=self.valid_cat_var,
            split_var=self.valid_cat_var,
            player=None
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_group_var(self):
        foo = HeroPerformanceChart(
            hero=self.valid_hero,
            game_mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            group_var=self.invalid_cat_var,
            split_var=self.valid_cat_var,
            player=None
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_split_var(self):
        foo = HeroPerformanceChart(
            hero=self.valid_hero,
            game_mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            group_var=self.valid_cat_var,
            split_var=self.invalid_cat_var,
            player=None
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_valid_call(self):
        foo = HeroPerformanceChart(
            hero=self.valid_hero,
            game_mode_list=self.valid_game_modes,
            x_var=self.valid_x_var,
            y_var=self.valid_y_var,
            group_var=self.valid_cat_var,
            split_var=self.valid_cat_var,
            player=None
        )
        self.assertNotEqual(foo.name, 'failface.png')


class HeroSkillBwTestCase(HeroValidityMixin, MatchValidityMixin, TestCase):
    fixtures = [
        'datadrivendota/heroes/test_data.json',
        'datadrivendota/matches/test_data.json'
    ]

    def setUp(self):
        User.objects.create_user(
            'temporary',
            'temporary@gmail.com',
            'temporary'
        )
        super(HeroSkillBwTestCase, self).setUp()

    def test_valid_call(self):
        foo = HeroSkillLevelBwChart(
            hero=self.valid_hero,
            player=None,
            game_mode_list=self.valid_game_modes,
            levels=self.valid_level_set
        )
        self.assertNotEqual(foo.name, 'failface.png')

    def test_invalid_hero(self):
        foo = HeroSkillLevelBwChart(
            hero=self.invalid_hero,
            player=None,
            game_mode_list=self.valid_game_modes,
            levels=self.valid_level_set
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_game_modes(self):
        foo = HeroSkillLevelBwChart(
            hero=self.valid_hero,
            player=None,
            game_mode_list=self.invalid_game_modes,
            levels=self.valid_level_set
        )
        self.assertEqual(foo.name, 'failface.png')

    def test_invalid_levels(self):
        foo = HeroSkillLevelBwChart(
            hero=self.valid_hero,
            player=None,
            game_mode_list=self.valid_game_modes,
            levels=self.invalid_level_set
        )
        self.assertEqual(foo.name, 'failface.png')
