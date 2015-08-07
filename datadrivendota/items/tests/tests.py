from django.test import TestCase, Client
from model_mommy import mommy
from items.management.commands.scrapeitemdata import Command as itemCommand


class TestUrlconf(TestCase):

    def setUp(self):
        self.item = mommy.make_recipe(
            'items.item', slug_name='dagon', cost=1
        )

    def test_urls_ok(self):
        c = Client()

        resp = c.get('/items/')
        self.assertEqual(resp.status_code, 200)

        resp = c.get('/items/dagon/')
        self.assertEqual(resp.status_code, 200)


class TestItemImport(TestCase):

    def setUp(self):
        self.command = itemCommand()
        self.data = self.command.dict_merge(
            self.command.name_dict(),
            self.command.site_json(),
        )

    def test_name_transform(self):

        self.assertEqual(
            self.command.get_name(
                'broadsword',
                self.data['broadsword']
            ),
            'Broadsword'
        )
        self.assertEqual(
            self.command.get_name(
                'blink',
                self.data['blink']
            ),
            'Blink Dagger'
        )
        self.assertEqual(
            self.command.get_name(
                'necronomicon_2',
                self.data['necronomicon_2']
            ),
            'Necronomicon 2'
        )
        self.assertEqual(
            self.command.get_name(
                'dagon',
                self.data['dagon']
            ),
            'Dagon 1'
        )

    def test_item_create(self):
        self.command.make_item('dagon_4', self.data['dagon_4'])

    def test_var_parse(self):
        cd = self.command.parse_var(
            {'long_name': 'AbilityCooldown', 'short_name': 'cd'},
            self.data['dagon_4'],
            'dagon_4'
        )
        self.assertEqual(cd, 20)

        cd = self.command.parse_var(
            {'long_name': 'AbilityCooldown', 'short_name': 'cd'},
            self.data['force_staff'],
            'force_staff'
        )
        self.assertEqual(cd, 20)

        cd = self.command.parse_var(
            {'long_name': 'AbilityCooldown', 'short_name': 'cd'},
            self.data['black_king_bar'],
            'black_king_bar'
        )
        self.assertEqual(cd, 80)
