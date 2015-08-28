from django.test import TestCase, Client
from model_mommy import mommy
from django.core.urlresolvers import reverse

from matches.viewsets import MatchPickBanViewSet
from matches.mommy_recipes import make_league_match
from matches.models import PickBan, Match, GameMode


# class TestUrlconf(TestCase):

#     @classmethod
#     def setUpClass(cls):
#         super(TestUrlconf, cls).setUpClass()
#         cls.match = mommy.make_recipe('matches.match')

#     def test_url_ok(self):
#         c = Client()

#         resp = c.get(reverse('matches:index'))
#         self.assertEqual(resp.status_code, 200)

#         resp = c.get(
#             reverse(
#                 'matches:detail',
#                 kwargs={'match_id': self.match.steam_id}
#             )
#         )
#         self.assertEqual(resp.status_code, 200)

#         resp = c.get(
#             reverse(
#                 'matches:detail',
#                 kwargs={'match_id': -1}
#             )
#         )
#         self.assertEqual(resp.status_code, 404)


class TestTrickyViewsets(TestCase):

    @classmethod
    def setUpClass(cls):

        super(TestTrickyViewsets, cls).setUpClass()
        make_league_match()

    def test_viewset_qs_values(self):
        matches = Match.objects.filter(
            game_mode__steam_id=2
        ).values('steam_id')
        pickban_qs = MatchPickBanViewSet()._get_pickban_queryset(matches)

        self.assertEqual(
            pickban_qs.count(),
            20
        )

        keyset = set([
            'pickban__order',
            'steam_id',
            'start_time',
            'pickban__team',
            'duration',
            'pickban__is_pick',
            'radiant_win',
            'pickban__hero__steam_id'
        ])

        for x in pickban_qs:
            self.assertEqual(set(x.keys()), keyset)

    def test_viewset_qs_refactor(self):
        matches = Match.objects.filter(
            game_mode__steam_id=2
        ).values('steam_id')
        pickban_qs = MatchPickBanViewSet()._get_pickban_queryset(matches)
        out = MatchPickBanViewSet()._refactor_pickbans(pickban_qs)
        self.assertEqual(len(out), 1)

        self.assertEqual(len(out), 1)
        match_keyset = set([
            'radiant_win',
            'steam_id',
            'start_time',
            'pickbans',
        ])
        self.assertEqual(set(out[0].keys()), match_keyset)
        self.assertEqual(len(out[0]['pickbans']), 20)

        pickban_keyset = set([
            'hero',
            'is_pick',
            'order',
            'team',
        ])

        hero_keyset = set([
            'steam_id',
        ])
        self.assertEqual(set(out[0]['pickbans'][0].keys()), pickban_keyset)
        self.assertEqual(
            set(out[0]['pickbans'][0]['hero'].keys()),
            hero_keyset
        )
