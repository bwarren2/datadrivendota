from django.test import TestCase, Client
from model_mommy import mommy

from ..models import PlayerMatchSummary
from ..management.parser_tasks import CreateMatchParse
from datadrivendota.management.tasks import ApiContext
from accounts.models import MatchRequest

# class TestModel(TestCase):

#     def setUp(self):
#         self.rad_win = mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__radiant_win=True,
#             player_slot=0
#         )
#         self.dire_win = mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__radiant_win=False,
#             player_slot=132
#         )
#         self.rad_loss = mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__radiant_win=False,
#             player_slot=0
#         )
#         self.dire_loss = mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__radiant_win=True,
#             player_slot=132
#         )
#         super(TestModel, self).setUp()

#     def test_wins(self):
#         self.assertEqual(self.rad_win.determine_win(), True)
#         self.assertEqual(self.dire_win.determine_win(), True)
#         self.assertEqual(self.rad_loss.determine_win(), False)
#         self.assertEqual(self.dire_loss.determine_win(), False)

#     def test_sides(self):
#         self.assertEqual(self.rad_win.side, 'Radiant')
#         self.assertEqual(self.dire_win.side, 'Dire')


# class TestUrlconf(TestCase):

#     @classmethod
#     def setUpClass(cls):
#         super(TestUrlconf, cls).setUpClass()
#         cls.match = mommy.make_recipe('matches.match')

#     def test_url_ok(self):
#         c = Client()

#         resp = c.get('/matches/')
#         self.assertEqual(resp.status_code, 200)

#         resp = c.get('/matches/{0}/'.format(self.match.steam_id))
#         self.assertEqual(resp.status_code, 200)

#         # resp = c.get('/matches/{0}/parse_match/'.format(self.match.steam_id))
#         # self.assertEqual(resp.status_code, 200)
#         # The template relies on a replay file, which breaks here.
#         # This is due for refactor during replay parsing.


# class FakeRequest(object):

#     def __init__(self, **kwargs):

#         self.query_params = kwargs

#     def __repr__(self):
#         return ','.join([
#             "{0}->{1}".format(str(x), str(y))
#             for x, y in self.query_params.iteritems()
#         ])


# class TestFakeRequest(TestCase):

#     def test_merge(self):
#         req = FakeRequest(page_size=10, player_id=103)
#         self.assertEqual(
#             req.query_params,
#             {
#                 'page_size': 10,
#                 'player_id': 103,
#             })


# class TestQuerySet(TestCase):

#     def test_player_filter(self):
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             player__steam_id=103,
#             _quantity=2
#         )
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             player__steam_id=2,
#         )

#         request = FakeRequest(player_id=103)
#         pmses = PlayerMatchSummary.objects.given(request)
#         self.assertEqual(pmses.count(), 2)

#     def test_validity_filter(self):
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__validity=1,
#             _quantity=2
#         )
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__validity=2,
#         )

#         request = FakeRequest(validity='LEGIT')
#         pmses = PlayerMatchSummary.objects.given(request)
#         self.assertEqual(pmses.count(), 2)

#     def test_hero_filter(self):
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             hero__steam_id=1,
#             _quantity=2
#         )
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             hero__steam_id=2,
#         )

#         request = FakeRequest(hero_id=1)
#         pmses = PlayerMatchSummary.objects.given(request)
#         self.assertEqual(pmses.count(), 2)

#     def test_league_filter(self):
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__league__steam_id=1,
#             _quantity=2
#         )
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__league__steam_id=2,
#         )

#         request = FakeRequest(league_id=1)
#         pmses = PlayerMatchSummary.objects.given(request)
#         self.assertEqual(pmses.count(), 2)

#     def test_skill_filter(self):
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__skill=1,
#             _quantity=2
#         )
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__skill=2,
#         )

#         request = FakeRequest(skill=1)
#         pmses = PlayerMatchSummary.objects.given(request)
#         self.assertEqual(pmses.count(), 2)

#     def test_team_filter(self):
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__radiant_team__steam_id=1,
#             _quantity=2
#         )
#         mommy.make_recipe(
#             'matches.playermatchsummary',
#             match__radiant_team__steam_id=2,
#         )

#         request = FakeRequest(team_id=1)
#         pmses = PlayerMatchSummary.objects.given(request)
#         self.assertEqual(pmses.count(), 2)


class TestParserTask(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestParserTask, cls).setUpClass()
        cls.match_id = 1615448703
        cls.match = mommy.make(
            'matches.Match',
            steam_id=cls.match_id
        )
        cls.match_request = mommy.make(
            'accounts.MatchRequest', match_id=cls.match_id
        )

    def test_match_check(self):
        task = CreateMatchParse()
        self.assertEqual(task.have_match(self.match.steam_id), True)

    def test_get_url(self):
        task = CreateMatchParse()
        task.have_match(self.match.steam_id)
        task.get_replay_url(self.match.steam_id)
        mr = MatchRequest.objects.get(match_id=self.match_id)
        self.assertNotEqual(mr.valve_replay_url, None)
