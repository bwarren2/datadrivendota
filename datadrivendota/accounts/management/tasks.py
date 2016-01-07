import logging
import time
import pika
import sys
import json
import requests
from io import BytesIO

from celery import Task, chain

from django.core.files import File
from django.conf import settings
from django.db.models import Q

from accounts.models import MatchRequest
from datadrivendota.management.tasks import ValveApiCall, ApiContext
from matches.management.tasks import UpdateMatch, UpdatePmsReplays
from matches.models import Match
from utils import gzip_str

logger = logging.getLogger(__name__)


class KickoffMatchRequests(Task):

    def run(self, only_use_submitted=True):
        match_requests = self.get_requests(only_use_submitted)
        logging.info('Got these match requests: {0}'.format(match_requests))
        for request in match_requests:
            self.chain_updates(request)
            self.mark_finding(request)

    def get_requests(self, only_use_submitted):
        if only_use_submitted:
            return MatchRequest.objects.filter(status=MatchRequest.SUBMITTED)
        else:
            return MatchRequest.objects.filter(
                Q(status=MatchRequest.SUBMITTED) |
                Q(status=MatchRequest.FINDING_MATCH) |
                Q(status=MatchRequest.MATCH_FOUND)
            )

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

            MatchRequest.objects.filter(
                match_id=match_id,
                status=MatchRequest.FINDING_MATCH
            ).update(
                status=MatchRequest.MATCH_FOUND
            )
            mr = MatchRequest.objects.get(match_id=match_id)
            return mr

        except Match.DoesNotExist:
            mr = MatchRequest.objects.filter(
                match_id=match_id
            ).update(
                status=MatchRequest.MATCH_NOT_FOUND
            )
            mr.save()
            return None

    def get_replay_url(self, match_id, match_req):

        url = settings.REPLAY_SERVICE_URL
        payload = {'match_id': match_id}
        r = requests.get(url, params=payload)
        logger.info('Hitting {1} with {0}'.format(payload, url))
        if r.status_code == 200:
            logger.info(r.content)
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
        logger.warning(
            'Creating match requests.  Queue durability is {0}'.format(
                settings.JAVA_QUEUE_DURABILITY
            )
        )
        result = channel.queue_declare(
            queue=queue_name,
            durable=settings.JAVA_QUEUE_DURABILITY,
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
        channel.basic_publish(
            exchange=queue_name,
            routing_key=queue_name,
            body=msg
        )
        logger.info(" [x] Sent {0}".format(msg))
        connection.close()


class ReadParseResults(Task):

    def run(self):
        connection = pika.BlockingConnection(
            pika.URLParameters(settings.BROKER_URL)
        )
        channel = connection.channel()
        queue_name = 'python_parse'
        channel.exchange_declare(
            exchange=queue_name,
            type='direct',
            durable=True
        )
        result = channel.queue_declare(
            queue=queue_name,
            durable=settings.JAVA_QUEUE_DURABILITY,
        )
        channel.queue_bind(
            exchange=queue_name,
            queue=result.method.queue,
            routing_key=queue_name
        )

        start = time.time()

        any_scheduled = False

        def drain(queue_name):

            method_frame, header_frame, body = channel.basic_get(queue_name)
            if not method_frame:
                return None
            else:
                MergeMatchRequestReplay().s().delay(json_data=json.loads(body))
                channel.basic_ack(method_frame.delivery_tag)

            return None

        while time.time() - start < 2:
            drain(queue_name)

        if any_scheduled:
            logger.info('Scheduled merge')

        channel.cancel()
        channel.close()
        connection.close()


class MergeMatchRequestReplay(Task):

    def run(self, json_data):

        match_id = json_data['match_id']
        filename = json_data['filename']

        logger.info('Merging {0}'.format(match_id))

        mr = MatchRequest.objects.get(match_id=match_id)
        self.merge_to_request(mr, filename)
        self.merge_to_match(mr, match_id)
        UpdatePmsReplays().delay(match_id=match_id)  # Queue for postprocessing

    def merge_to_match(self, mr, match_id):
        match = Match.objects.get(steam_id=match_id)
        mr = MatchRequest.objects.get(match_id=match_id)
        url = mr.file_url
        try:
            r = requests.get(url)
            if r.status_code == 200:
                holder = BytesIO(r.content)
                _ = holder.seek(0)  # NOQA
                filename = "{0}_parse.json".format(match_id)
                match.replay.save(filename, File(holder))

                holder = BytesIO(gzip_str(r.content))
                _ = holder.seek(0)  # NOQA
                filename = "{0}_parse.json.gz".format(match_id)
                match.compressed_replay.save(filename, File(holder))

            else:
                logger.info(
                    "Could not get the replay {0}!  Error code {1}".format(
                        url, r.status_code
                    )
                )
        except:
            err = sys.exc_info()[0]
            logger.info(
                "Replay parsing error for  %s!  Error %s" % (match_id, err)
            )

    def merge_to_request(self, match_request, filename):
        match_request.raw_parse_url = filename
        match_request.status = MatchRequest.PARSED
        match_request.save()
