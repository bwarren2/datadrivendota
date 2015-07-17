import pika
import json
import requests
from django.conf import settings
from celery import Task

from ..models import Match
from accounts.models import MatchRequest


class CreateMatchParse(Task):

    def run(self, api_context):
        match_id = api_context.match_id

        got_match = self.have_match(match_id)
        if got_match:
            replay_url = self.get_replay_url(match_id)
            self.java_parse_message(replay_url, match_id)
        else:
            raise Exception("We don't have the match we expected: {0}".format(
                self.match_id
            ))

    def have_match(self, match_id):
        try:
            Match.objects.get(steam_id=match_id)

            mr = MatchRequest.objects.get(
                match_id=match_id,
                status=MatchRequest.FINDING_MATCH
            )

            mr.status = MatchRequest.MATCH_FOUND
            mr.save()

            # Hold for later
            self.match_request = mr
            return True

        except Match.DoesNotExist:
            mr = MatchRequest.objects.get(steam_id=match_id)
            mr.status = MatchRequest.MATCH_NOT_FOUND
            mr.save()
            return False

    def get_replay_url(self, match_id):

        url = settings.REPLAY_SERVICE_URL
        payload = {'match_id': match_id}
        print url
        r = requests.get(url, params=payload)
        if r.status_code == 200:
            replay_url = r.json()['replay_url']
            self._save_url(replay_url, self.match_request)

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

        channel.queue_declare(queue='java_parse')
        msg = json.dumps({
            'url': url,
            'match_id': match_id,
        })
        channel.basic_publish(exchange='',
                              routing_key='java_parse',
                              body=msg)
        print " [x] Sent {0}".format(msg)
        connection.close()
