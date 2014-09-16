from django.test import TestCase
from django.forms import ValidationError

from .factories import HeroFactory, HeroDossierFactory
from heroes.models import Hero
from utils import safen
from heroes.form_fields import SingleHeroSelect, MultiHeroSelect
from heroes.json_data import hero_vitals_json, hero_lineup_json
from utils.exceptions import NoDataFound


class TestBase(TestCase):

    def setUp(self):
        pass

    def test_add(self):
        self.assertEqual(2+2, 4)


class TestHeroes(TestCase):

    def setUp(self):
        self.hero = HeroFactory(name=u'Axe')

    def test_names(self):
        self.assertEqual(self.hero.__unicode__(), self.hero.name)
        self.assertEqual(self.hero.safe_name(), safen(self.hero.machine_name))


class TestHeroManagers(TestCase):

    def setUp(self):
        self.heroes = HeroFactory.create_batch(10)

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
        self.hero = HeroFactory(steam_id=1)

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
        self.hero = HeroFactory(steam_id=1)
        HeroFactory(steam_id=2)

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
        h1 = HeroFactory(steam_id=1)
        h2 = HeroFactory(steam_id=2)
        HeroDossierFactory(hero=h1)
        HeroDossierFactory(hero=h2)

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
        h1 = HeroFactory(steam_id=1)
        h2 = HeroFactory(steam_id=2)
        HeroDossierFactory(hero=h1)
        HeroDossierFactory(hero=h2)

    def tearDown(self):
        pass

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


class TestPerformanceJson(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_working_json(self):
        pass  # Needs more factories


class TestProgressionJson(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_working_json(self):
        pass  # Needs more factories


class TestSkillbuildJson(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_working_json(self):
        pass  # Needs more factories


class TestWinrateJson(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_working_json(self):
        pass  # Needs more factories


class TestPerformanceLineupJson(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_working_json(self):
        pass  # Needs more factories


class TestPickWinrateJson(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_working_json(self):
        pass  # Needs more factories
