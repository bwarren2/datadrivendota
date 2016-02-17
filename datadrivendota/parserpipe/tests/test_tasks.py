
import responses
from model_mommy import mommy

from django.test import TestCase
from django.db.models import Q
from django.utils.decorators import method_decorator

from parserpipe.management.tasks import (
    KickoffMatchRequests, CreateMatchParse, UpdatePmsReplays, UpdateParseEnd
)

from parserpipe.models import MatchRequest

from .json_samples import all_income


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

    def test_match_check(self):
        task = CreateMatchParse()
        self.assertEqual(
            task.have_match(self.match.steam_id),
            self.match_request
        )

    @method_decorator(responses.activate)
    def test_get_url(self):
        responses.add(
            responses.GET,
            'https://replayurls.herokuapp.com/tools/matchurls?match_id=1615448703',
             body='{"replay_url": "http://replay121.valve.net/570/1615448703_975041684.dem.bz2"}',
            status=200,
            content_type='application/json',
            match_querystring=True,
        )

        task = CreateMatchParse()
        match_req = task.have_match(self.match.steam_id)
        task.get_replay_url(self.match.steam_id, match_req)
        mr = MatchRequest.objects.get(match_id=self.match_id)
        self.assertNotEqual(mr.valve_replay_url, None)


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
