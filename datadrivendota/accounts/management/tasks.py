import time
import pika
import json
import requests
from celery import Task, chain
from accounts.models import MatchRequest
from datadrivendota.management.tasks import ValveApiCall, ApiContext
from matches.management.tasks import UpdateMatch
from django.conf import settings

from matches.models import Match


class KickoffMatchRequests(Task):

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
        chain(
            vac.s(api_context=c, mode='GetMatchDetails'),
            um.s(),
            cmp.s()
        ).delay()

    def mark_finding(self, request):
        request.status = MatchRequest.FINDING_MATCH
        request.save()


class CreateMatchParse(Task):

    def run(self, api_context):
        match_id = api_context.match_id

        match_req = self.have_match(match_id)

        if match_req:
            replay_url = self.get_replay_url(match_id, match_req)

            if replay_url:
                self.java_parse_message(replay_url, match_id)
        else:
            raise Exception("We don't have the match we expected: {0}".format(
                self.match_id
            ))

    def have_match(self, match_id):
        """ Return the match request if we have its match. """
        try:
            Match.objects.get(steam_id=match_id)

            mr = MatchRequest.objects.get(
                match_id=match_id,
                status=MatchRequest.FINDING_MATCH
            )

            mr.status = MatchRequest.MATCH_FOUND
            mr.save()

            return mr

        except Match.DoesNotExist:
            mr = MatchRequest.objects.get(steam_id=match_id)
            mr.status = MatchRequest.MATCH_NOT_FOUND
            mr.save()
            return None

    def get_replay_url(self, match_id, match_req):

        url = settings.REPLAY_SERVICE_URL
        payload = {'match_id': match_id}
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            replay_url = r.json()['replay_url']
            self._save_url(replay_url, match_req)

            return replay_url

        else:
            raise Exception("Got status {0} for MR match_id {1}".format(
                r.status_code, match_id
            ))
            return None

    def _save_url(self, url, match_request):
        match_request.valve_replay_url = url
        match_request.save()

    def java_parse_message(self, url, match_id):
        """ Push the data into the java queue. """
        connection = pika.BlockingConnection(
            pika.URLParameters(
                settings.BROKER_URL
            )
        )
        channel = connection.channel()
        queue_name = 'java_parse'
        channel.exchange_declare(exchange=queue_name, type='direct')
        result = channel.queue_declare(
            queue=queue_name,
            durable=True,
        )
        channel.queue_bind(
            exchange=queue_name,
            queue=result.method.queue,
            routing_key=queue_name
        )
        msg = json.dumps({
            'url': url,
            'match_id': match_id,
        })
        channel.basic_publish(exchange=queue_name,
                              routing_key=queue_name,
                              body=msg)
        print " [x] Sent {0}".format(msg)
        connection.close()


class ReadParseResults(Task):

    def run(self):
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.BROKER_URL)
        )
        channel = connection.channel()
        queue_name = 'python_parse'
        channel.exchange_declare(exchange=queue_name, type='direct')
        result = channel.queue_declare(
            queue=queue_name,
            durable=True,
        )
        channel.queue_bind(
            exchange=queue_name,
            queue=result.method.queue,
            routing_key=queue_name
        )

        start = time.time()

        def drain(queue_name):
            # {"filename":"1652732189_parse.json","match_id":1652732189}

            method_frame, header_frame, body = channel.basic_get(queue_name)
            if not method_frame:
                return None
            else:
                MergeMatchRequestReplay().s().delay(json_data=json.loads(body))
                channel.basic_ack(method_frame.delivery_tag)

            return None

        while time.time() - start < 2:
            drain(queue_name)

        channel.cancel()
        channel.close()
        connection.close()


class MergeMatchRequestReplay(Task):

    def run(self, json_data):
        print json_data
        match_id = json_data['match_id']
        mr = MatchRequest.objects.get(match_id=match_id)
        mr.raw_parse_url = json_data['filename']
        mr.status = MatchRequest.PARSED
        mr.save()
