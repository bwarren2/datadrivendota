from collections import defaultdict
from django.templatetags.static import static
from django.test import TestCase, Client
from model_mommy import mommy
from items.management.commands.scrapeitemdata import Command as itemCommand
from items.management.tasks import UpdateItemSchema


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


class TestModel(TestCase):

    def test_mugshot(self):

        i = mommy.make('items.item', mugshot=None)
        self.assertEqual(i.mugshot_url, static('blanks/blank_item.png'))
        i.delete()

        i = mommy.make('items.item')
        self.assertNotEqual(i.mugshot_url, static('blanks/blank_item.png'))
        i.delete()

    def test_thumbshot(self):

        i = mommy.make('items.item', thumbshot=None)
        self.assertEqual(
            i.thumbshot_url,
            static('blanks/blank_item_small.png')
        )
        i.delete()

        i = mommy.make('items.item')
        self.assertNotEqual(
            i.thumbshot_url,
            static('blanks/blank_item_small.png')
        )
        i.delete()


class TestJsonStorage(TestCase):

    def test_strip(self):
        wrapped_data = {
            'items_game': {
                'items': {}
            }
        }
        test_data = {
                    u'creation_date': u'2015-12-02',
                    u'event_id': u'EVENT_ID_NONE',
                    u'image_banner':
                    u'econ/leagues/subscriptions_winter_major_2016_ingame',
                    u'image_inventory':
                    u'econ/leagues/subscriptions_winter_major_2016',
                    u'item_description': u'#DOTA_Item_Desc_Shanghai_Major',
                    u'item_name': u'#DOTA_Item_Shanghai_Major',
                    u'item_rarity': u'mythical',
                    u'item_type_name': u'#DOTA_WearableType_Ticket',
                    u'name': u'Shanghai Major',
                    u'prefab': u'league',
                    u'tool': {
                        u'type': u'league_view_pass',
                        u'usage': {
                            u'end_date': u'1457251200',
                            u'free_to_spectate': u'1',
                            u'league_id': u'4266',
                            u'order': u'3708',
                            u'start_date': u'1456905600',
                            u'tier': u'premium'
                        },
                        u'use_string': u'#ConsumeItem'},
                    u'tournament_url': u'http://www.dota2.com'
                    }
        wrapped_data['items_game']['items']['16807'] = test_data
        task = UpdateItemSchema()

        self.assertEqual(
            {'16807': test_data}, task.strip_wrapper(wrapped_data)
        )

    def test_filter(self):
        test_data = {
                    '16807': {
                        u'creation_date': u'2015-12-02',
                        u'event_id': u'EVENT_ID_NONE',
                        u'image_banner':
                        u'econ/leagues/subscriptions_winter_major_2016_ingame',
                        u'image_inventory':
                        u'econ/leagues/subscriptions_winter_major_2016',
                        u'item_description': u'#DOTA_Item_Desc_Shanghai_Major',
                        u'item_name': u'#DOTA_Item_Shanghai_Major',
                        u'item_rarity': u'mythical',
                        u'item_type_name': u'#DOTA_WearableType_Ticket',
                        u'name': u'Shanghai Major',
                        u'prefab': u'league',
                        u'tool': {
                            u'type': u'league_view_pass',
                            u'usage': {
                                u'end_date': u'1457251200',
                                u'free_to_spectate': u'1',
                                u'league_id': u'4266',
                                u'order': u'3708',
                                u'start_date': u'1456905600',
                                u'tier': u'premium'
                            },
                            u'use_string': u'#ConsumeItem'},
                        u'tournament_url': u'http://www.dota2.com'
                        },
                    '2': {
                        u'creation_date': u'2015-12-02',
                        u'event_id': u'EVENT_ID_NONE',
                        u'image_banner':
                        u'econ/leagues/subscriptions_winter_major_2016_ingame',
                        u'image_inventory':
                        u'econ/leagues/subscriptions_winter_major_2016',
                        u'item_description': u'#DOTA_Item_Desc_Shanghai_Major',
                        u'item_name': u'#DOTA_Item_Shanghai_Major',
                        u'item_rarity': u'mythical',
                        u'item_type_name': u'#DOTA_WearableType_Ticket',
                        u'name': u'Shanghai Major',
                        u'prefab': u'league',
                        u'tool': {
                            u'type': u'league_view_pass',
                            u'use_string': u'#ConsumeItem'},
                        u'tournament_url': u'http://www.dota2.com'
                        }
                }
        task = UpdateItemSchema()
        self.assertEqual(
            task.get_leagues(test_data),
            {4266: test_data['16807']}
        )
