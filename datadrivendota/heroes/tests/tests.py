from django.templatetags.static import static
from django.test import TestCase, Client
from django.forms import ValidationError
from model_mommy import mommy

from heroes.models import Hero
from utils import safen
from heroes.form_fields import SingleHeroSelect, MultiHeroSelect
from heroes.mommy_recipes import make_hero

JSON_TIME = 2

# update_player_winrate uses 1.5s cap, needs optimization


class TestHeroes(TestCase):

    def setUp(self):
        self.hero = mommy.make('heroes.hero', name=u'Axe')

    def test_names(self):
        self.assertEqual(self.hero.__unicode__(), self.hero.name)
        self.assertEqual(self.hero.safe_name(), safen(self.hero.machine_name))

    def test_mugshot(self):

        h = mommy.make('heroes.hero', mugshot=None)
        self.assertEqual(
            h.mugshot_url,
            static('blanks/blank_hero_mugshot.png')
        )
        h.delete()

        h = mommy.make('heroes.hero')
        self.assertNotEqual(
            h.mugshot_url,
            static('blanks/blank_hero_mugshot.png')
        )
        h.delete()

    def test_thumbshot(self):

        h = mommy.make('heroes.hero', thumbshot=None)
        self.assertEqual(
            h.thumbshot_url,
            static('blanks/blank_hero_thumb.png')
        )
        h.delete()

        h = mommy.make('heroes.hero')
        self.assertNotEqual(
            h.thumbshot_url,
            static('blanks/blank_hero_thumb.png')
        )
        h.delete()

    def test_has_image(self):

        h = mommy.make('heroes.hero', thumbshot=None)
        self.assertEqual(h.has_image, False)
        h.delete()

        h = mommy.make('heroes.hero')
        self.assertEqual(h.has_image, True)
        h.delete()


class TestMommyRecipes(TestCase):

    def setUp(self):
        pass

    def test_fake(self):
        mommy.make_recipe('heroes.hero', name=u'Axe')
        make_hero()


class TestHeroManagers(TestCase):

    @classmethod
    def setUpClass(cls):
        super(cls, TestHeroManagers).setUpClass()     # Call parent first
        Hero.objects.all().delete()
        cls.heroes = mommy.make_recipe('heroes.hero', _quantity=10)

    @classmethod
    def tearDownClass(cls):
        Hero.objects.all().delete()
        super(cls, TestHeroManagers).tearDownClass()  # Call parent last

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


class TestUrlconf(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUrlconf, cls).setUpClass()
        cls.hero_doss = mommy.make_recipe(
            'heroes.herodossier', hero__machine_name='natures-prophet'
        )

    def test_url_ok(self):

        c = Client()

        resp = c.get('/heroes/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/heroes/vitals/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/heroes/lineups/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/heroes/{0}/'.format(self.hero_doss.hero.machine_name))
        self.assertEqual(resp.status_code, 200)
        # Almost all the other urls are to be gutted, so we are done here.


class TestRoles(TestCase):

    def test_thumbshot(self):

        h = mommy.make('heroes.role', thumbshot=None)
        self.assertEqual(
            h.thumbshot_url,
            static('blanks/blank_role.png')
        )
        h.delete()

        h = mommy.make('heroes.role', thumbshot='hi.png')
        self.assertNotEqual(
            h.thumbshot_url,
            static('blanks/blank_role.png')
        )
        h.delete()


class TestAbility(TestCase):

    def test_thumbshot(self):

        ability = mommy.make('heroes.ability', picture=None)
        self.assertEqual(
            ability.image_url,
            static('blanks/blank_ability.png')
        )
        ability.delete()
