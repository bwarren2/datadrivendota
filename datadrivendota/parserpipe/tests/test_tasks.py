
import time
from model_mommy import mommy
from datetime import timedelta

from django.test import TestCase
from django.db.models import Q
from django.utils import timezone

from parserpipe.management.tasks import (
    KickoffMatchRequests,
    CreateMatchParse,
    UpdatePmsReplays,
    UpdateParseEnd,
    CreateMatchRequests
)
from matches.models import Match
from parserpipe.models import MatchRequest

from .json_samples import all_income, bot_match_details


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
            'parserpipe.MatchRequest',
            match_id=cls.match_id,
            status=MatchRequest.FINDING_MATCH
        )

    def test_make_match(self):
        match_id = 2410589774
        CreateMatchParse().make_match(bot_match_details, match_id)
        url = Match.objects.get(steam_id=match_id).replay_url
        self.assertEqual(
            url,
            "http://replay134.valve.net/570/2410589774_1651935664.dem.bz2"
        )


class TestKickoffRequestTask(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestKickoffRequestTask, cls).setUpClass()
        mommy.make(
            'parserpipe.MatchRequest',
            status=MatchRequest.SUBMITTED,
            _quantity=2
        )
        mommy.make(
            'parserpipe.MatchRequest',
            status=MatchRequest.FINDING_MATCH,
        )
        mommy.make(
            'parserpipe.MatchRequest',
            status=MatchRequest.MATCH_FOUND,
        )
        mommy.make(
            'parserpipe.MatchRequest',
            status=MatchRequest.MATCH_FOUND,
        )
        mommy.make(
            'parserpipe.MatchRequest',
            status=MatchRequest.COMPLETE,
        )

    def test_get_requests(self):

        # Test only pushing submitted requests
        self.assertQuerysetEqual(
            MatchRequest.objects.filter(
                status=MatchRequest.SUBMITTED
            ).order_by('id'),
            map(repr, KickoffMatchRequests().get_requests(True).order_by('id'))
        )

        # Test when we want to force along everything, not just submitted
        self.assertQuerysetEqual(
            MatchRequest.objects.filter(
                Q(status=MatchRequest.SUBMITTED) |
                Q(status=MatchRequest.FINDING_MATCH) |
                Q(status=MatchRequest.MATCH_FOUND)
            ).order_by('id'),
            map(repr, KickoffMatchRequests().get_requests(
                False
            ).order_by('id'))
        )

    def test_marked(self):
        requests = KickoffMatchRequests().get_requests(True)
        for request in requests:
            KickoffMatchRequests().mark_finding(request)
            self.assertEqual(request.status, MatchRequest.FINDING_MATCH)


class TestShardMunging(TestCase):

    def test_timeseries(self):

        t = UpdatePmsReplays()
        output = t.timeseries_combat(
            {'all_income': all_income}, 234, 236, 235
        )
        self.assertEqual(
            output,
            {
                'all_income':
                [
                    {'all_income': 625, 'offset_time': -1, 'time': 234},
                    {'all_income': 625, 'offset_time': 0, 'time': 235},
                    {'all_income': 965, 'offset_time': 1, 'time': 236}
                ]
            }
        )


class TestAggregateDataseries(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.test_shards = [
            [
                {'all_income': 624, 'offset_time': -2, 'time': 233},
                {'all_income': 625, 'offset_time': -1, 'time': 234},
                {'all_income': 625, 'offset_time': 0, 'time': 235},
                {'all_income': 965, 'offset_time': 1, 'time': 236}
            ],
            [
                {'all_income': 1, 'offset_time': -1, 'time': 234},
                {'all_income': 2, 'offset_time': 0, 'time': 235},
                {'all_income': 3, 'offset_time': 1, 'time': 236}
            ],
        ]
        cls.test_hashed = [
            {
                -2: 624,
                -1: 625,
                0: 625,
                1: 965
            },
            {
                -1: 1,
                0: 2,
                1: 3
            },
        ]
        super(TestAggregateDataseries, cls).setUpClass()

    def test_hashing(self):
        t = UpdateParseEnd()
        actual = t.rehash(self.test_shards, 'all_income')
        expect = self.test_hashed
        self.assertEqual(actual, expect)

    def test_counting(self):
        t = UpdateParseEnd()

        inputs = self.test_hashed
        actual = t.extract_keys(inputs)
        expect = [-1, 0, 1]

        self.assertEqual(actual, expect)

    def test_counting_discontinuous(self):
        t = UpdateParseEnd()

        inputs = [
            {
                -1: 625,
                1: 965
            },
            {
                -1: 1,
                1: 3
            },
        ]

        with self.assertRaises(ValueError):
            t.extract_keys(inputs)

    def test_sum_aggregate(self):
        t = UpdateParseEnd()
        data_sum = t.rollup_dataseries(self.test_shards, 'all_income', 'sum')
        self.assertEqual(
            data_sum,
            [
                {'all_income': 626, 'offset_time': -1},
                {'all_income': 627, 'offset_time': 0},
                {'all_income': 968, 'offset_time': 1}
            ]
        )

    def test_diff_aggregate(self):
        t = UpdateParseEnd()
        data_sum = t.rollup_dataseries(self.test_shards, 'all_income', 'diff')
        self.assertEqual(
            data_sum,
            [
                {'all_income': 624, 'offset_time': -1},
                {'all_income': 623, 'offset_time': 0},
                {'all_income': 962, 'offset_time': 1}
            ]
        )

    def test_allstate_diff(self):
        t = UpdateParseEnd()
        data_sum = t.rollup_dataseries(self.test_shards, 'allstate', 'diff')
        self.assertEqual(
            data_sum,
            [
                {'all_income': 624, 'offset_time': -1, 'time': 0},
                {'all_income': 623, 'offset_time': 0, 'time': 0},
                {'all_income': 962, 'offset_time': 1, 'time': 0}
            ]
        )

    def test_combatseries_merge(self):
        test_data = {
            'kills': [{'time': 1, 'kills': 1}, {'time': 2, 'kills': 1}],
            'deaths': [{'time': 1, 'deaths': 1}, {'time': 2, 'deaths': 1}],
        }
        t = UpdatePmsReplays()
        got = t.merge_combatseries_dicts(0, test_data)
        expected = {'deaths': 1, 'kills': 1, 'time': 1}
        self.assertEqual(got, expected)


class TestMatchRequestCreation(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestMatchRequestCreation, cls).setUpClass()
        cls.since = timezone.now() - timedelta(days=1)
        cls.client_steam_id = 1000000
        cls.non_client_steam_id = 999999
        cls.client_ids = [cls.client_steam_id]
        cls.client_player = mommy.make_recipe(
            'players.player', steam_id=cls.client_steam_id
        )
        cls.non_client_player = mommy.make_recipe(
            'players.player', steam_id=cls.non_client_steam_id
        )

        recent_start_time = time.mktime(timezone.now().timetuple())
        cls.recent_match = mommy.make_recipe(
            'matches.match',
            steam_id=22,
            parsed_with=None,
            start_time=recent_start_time
        )
        cls.recent_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            match=cls.recent_match,
            player=cls.client_player
        )

        distant_dt = timezone.now() - timedelta(weeks=10)
        distant_start_time = time.mktime(distant_dt.timetuple())
        cls.distant_match = mommy.make_recipe(
            'matches.match',
            steam_id=11,
            parsed_with=None,
            start_time=distant_start_time
        )
        cls.recent_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            match=cls.distant_match,
            player=cls.client_player
        )

        cls.nonclient_match = mommy.make_recipe(
            'matches.match',
            steam_id=33,
            parsed_with=None,
            start_time=recent_start_time
        )
        cls.recent_pms = mommy.make_recipe(
            'matches.playermatchsummary',
            match=cls.nonclient_match,
            player=cls.non_client_player
        )

    def test_match_discovery(self):
        task = CreateMatchRequests()
        found = task.get_match_ids(self.client_ids, self.since)
        self.assertEqual(list(found), [22])


# class TestUpdateParseEnd(TestCase):
#     task = UpdateParseEnd

#     def test_shardstate(self):
#         self.task().aggregate_shards(2288796036, 'allstate', 'statelog')
