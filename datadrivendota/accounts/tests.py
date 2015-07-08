from django.test import TestCase
from model_mommy import mommy
from .models import MatchRequest
from .management.tasks import UpdateMatchRequests
# Create your tests here.


class TestUpdateRequestTask(TestCase):

    @classmethod
    def setUpClass(cls):
        super(TestUpdateRequestTask, cls).setUpClass()
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.SUBMITTED,
            _quantity=2
        )
        mommy.make(
            'accounts.MatchRequest',
            status=MatchRequest.FINDING_MATCH,
        )

    def test_get_requests(self):
        self.assertQuerysetEqual(
            MatchRequest.objects.filter(
                status=MatchRequest.SUBMITTED
            ).order_by('id'),
            map(repr, UpdateMatchRequests().get_requests().order_by('id'))
        )

    def test_marked(self):
        requests = UpdateMatchRequests().get_requests()
        for request in requests:
            UpdateMatchRequests().mark_finding(request)
            self.assertEqual(request.status, MatchRequest.FINDING_MATCH)
