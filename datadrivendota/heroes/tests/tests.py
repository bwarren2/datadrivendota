from nose.tools import timed
from django.test import TestCase
from django.forms import ValidationError
from model_mommy import mommy

from heroes.models import Hero
from matches.models import GameMode
from utils import safen
from heroes.form_fields import SingleHeroSelect, MultiHeroSelect
from heroes.json_data import (
    hero_vitals_json,
    hero_lineup_json,
    hero_performance_chart_json,
    hero_progression_json,
    hero_skillbuild_winrate_json,
    update_player_winrate,
    hero_performance_lineup,
    )
from matches.mommy_recipes import make_matchset
from heroes.mommy_recipes import make_hero
from utils.exceptions import NoDataFound

JSON_TIME = .5

# update_player_winrate uses 1.5s cap, needs optimization


class TestHeroes(TestCase):

    def setUp(self):
        self.hero = mommy.make('heroes.hero', name=u'Axe')

    def test_names(self):
        self.assertEqual(self.hero.__unicode__(), self.hero.name)
        self.assertEqual(self.hero.safe_name(), safen(self.hero.machine_name))


class TestMommyRecipes(TestCase):

    def setUp(self):
        pass

    def test_fake(self):
        mommy.make_recipe('heroes.hero', name=u'Axe')
        make_hero()


class TestHeroManagers(TestCase):

    def setUp(self):
        self.heroes = mommy.make_recipe('heroes.hero', _quantity=10)

    def test_all(self):
        self.assertEqual(Hero.objects.all().count(), 10)

    def test_visibility(self):
        h = Hero.objects.all()[0]
        h.visible = False
        h.save()
        self.assertEqual(Hero.public.all().count(), 9)
        self.assertEqual(Hero.objects.filter(visible=False).count(), 1)


class TestSingleFormField(TestCase):

    def setUp(self):
        self.optional = SingleHeroSelect(required=False)
        self.required = SingleHeroSelect(required=True)
        self.hero = mommy.make_recipe('heroes.hero', steam_id=1)

    def test_single_hero(self):
        with self.assertRaises(ValidationError):
            self.required.clean(None)
        self.assertEqual(self.optional.clean(None), None)

        with self.assertRaises(ValidationError):
            self.required.clean('10,')

        checked_id = self.required.clean('1')
        Hero.objects.get(steam_id=checked_id)

        with self.assertRaises(ValidationError):
            self.required.clean('100')


class TestMultiFormField(TestCase):

    def setUp(self):
        self.optional = MultiHeroSelect(required=False)
        self.required = MultiHeroSelect(required=True)
        self.hero = mommy.make_recipe('heroes.hero', steam_id=1)
        mommy.make_recipe('heroes.hero', steam_id=2)

    def test_multi_hero(self):
        with self.assertRaises(ValidationError):
            self.required.clean(None)
        self.assertEqual(self.optional.clean(None), None)

        with self.assertRaises(ValidationError):
            self.required.clean('10,')

        checked_id = self.required.clean('1')
        ct = Hero.objects.filter(steam_id__in=checked_id).count()
        self.assertEqual(ct, 1)

        checked_id = self.required.clean('1,2')
        ct = Hero.objects.filter(steam_id__in=checked_id).count()
        self.assertEqual(ct, 2)

        with self.assertRaises(ValidationError):
            self.required.clean('100')


class TestVitalsJson(TestCase):

    def setUp(self):
        make_hero(steam_id=1)
        make_hero(steam_id=2)

    @timed(JSON_TIME)
    def test_working_json(self):
        """If these raise exceptions, that would be bad"""

        chart = hero_vitals_json(heroes=[1], stats=['strength'])
        self.assertGreater(len(chart.datalist), 10)
        chart = hero_vitals_json(heroes=[1, 2], stats=['strength'])
        self.assertGreater(len(chart.datalist), 10)
        chart = hero_vitals_json(heroes=[1, 2], stats=['strength', 'agility'])
        self.assertGreater(len(chart.datalist), 10)

    def test_broken_json(self):
        with self.assertRaises(NoDataFound):
            hero_vitals_json(heroes=[], stats=['strength'])
        with self.assertRaises(NoDataFound):
            hero_vitals_json(heroes=[1], stats=['bink'])


class TestLineupJson(TestCase):

    def setUp(self):
        make_hero(steam_id=1)
        make_hero(steam_id=2)

    def tearDown(self):
        pass

    @timed(JSON_TIME)
    def test_working_json(self):
        """If these raise exceptions, that would be bad"""

        chart = hero_lineup_json(heroes=[1, 2], stat='strength', level=2)
        self.assertGreater(len(chart.datalist), 1)
        chart = hero_lineup_json(heroes=[], stat='strength', level=2)
        self.assertGreater(len(chart.datalist), 1)

    def test_broken_json(self):
        with self.assertRaises(NoDataFound):
            hero_lineup_json(heroes=[], stat='stren', level=2)
        with self.assertRaises(NoDataFound):
            hero_lineup_json(heroes=[], stat='strength', level=26)


class TestWorkingJson(TestCase):

    @classmethod
    def setUpClass(self):
        self.hero, self.player = make_matchset()
        self.player.updated = True

    @timed(JSON_TIME)
    def test_performance_json(self):
        chart = hero_performance_chart_json(
            self.hero.steam_id,
            self.player.steam_id,
            x_var='duration',
            y_var='kills',
            group_var=None,
            panel_var=None,
            game_modes=None,
            matches=None,
            outcome='both',
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_progression_json(self):
        chart = hero_progression_json(
            self.hero.steam_id,
            self.player.steam_id,
            division='Skill',
            game_modes=None,
            matches=None,
            outcome=None,
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_skillbuild_json(self):
        chart = hero_skillbuild_winrate_json(
            self.hero.steam_id,
            self.player.steam_id,
            game_modes=None,
            levels=[1, 3],
        )
        self.assertGreater(len(chart.datalist), 1)

    @timed(1.5)
    def test_winrate_json(self):
        chart = update_player_winrate(
            self.hero.steam_id,
            game_modes=GameMode.objects.all(),
        )
        self.assertEqual(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_performance_lineup_json(self):
        chart = hero_performance_lineup(
            stat='kills',
            skill_level=1,
            outcome='win',
            heroes=[],
            min_date=None,
            max_date=None,
        )
        self.assertEqual(len(chart.datalist), 1)

    @timed(JSON_TIME)
    def test_pick_winrate_json(self):
        pass
