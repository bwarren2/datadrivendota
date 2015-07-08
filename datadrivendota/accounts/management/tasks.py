from celery import Task, chain
from accounts.models import MatchRequest
from datadrivendota.management.tasks import ValveApiCall, ApiContext
from matches.management.tasks import UpdateMatch
from matches.management.parser_tasks import CreateMatchParse


class UpdateMatchRequests(Task):

    def run(self):
        requests = self.get_requests()
        for request in requests:
            self.chain_updates(request)
            self.mark_finding(request)

    def get_requests(self):
        return MatchRequest.objects.filter(status=MatchRequest.SUBMITTED)

    def chain_updates(self, request):
        c = ApiContext()
        c.match_id = request.match_id
        vac = ValveApiCall()
        um = UpdateMatch()
        cmp = CreateMatchParse()
        print "Foo"
        chain(
            vac.s(api_context=c, mode='GetMatchDetails'),
            um.s(),
            cmp.s()
        ).delay()

    def mark_finding(self, request):
        request.status = MatchRequest.FINDING_MATCH
        request.save()
