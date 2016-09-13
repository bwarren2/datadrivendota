import logging
import time
import pika
import json
from datetime import timedelta

from celery import Task

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from parserpipe.models import MatchRequest
from datadrivendota.management.tasks import ApiContext
from matches.management.tasks import UpdateMatch
from matches.models import Match
from accounts.models import get_customer_player_ids
from leagues.models import League
from replay_url_broker.models import ReplayUrlBackend

logger = logging.getLogger(__name__)

logging.getLogger('pika').setLevel(logging.WARNING)


class CreateMatchRequests(Task):

    def run(self, days=1):
        since = timezone.now() - timedelta(days=days)
        client_ids = self.get_player_ids()
        matches = self.get_match_ids(client_ids, since)
        self.make_match_requests(matches)
        self.recur_match_requests()

    def get_player_ids(self):
        return get_customer_player_ids()

    def get_match_ids(self, client_ids, since):
        since_time = time.mktime(since.timetuple())

        unparsed_client_matches = Match.unparsed.filter(
            playermatchsummary__player__steam_id__in=client_ids,
            start_time__gte=since_time
        ).values_list('steam_id', flat=True)

        major_matches = Match.unparsed.filter(
            league__steam_id__in=[4266],
            start_time__gte=since_time
        ).values_list('steam_id', flat=True)

        premium_matches = Match.unparsed.filter(
            league__tier=League.PREMIUM,
            start_time__gte=since_time
        ).values_list('steam_id', flat=True)

        return_matches = list(unparsed_client_matches)
        return_matches.extend(list(major_matches))
        return_matches.extend(list(premium_matches))
        return return_matches

    def make_match_requests(self, matches):

        any_created = False
        for match in matches:
            mr, created = MatchRequest.objects.get_or_create(match_id=match)
            if created:
                any_created = True
                logger.info('MatchRequest created for {0}'.format(mr))

        if any_created:
            KickoffMatchRequests().delay()

    def recur_match_requests(self):
        since = timezone.now() - timedelta(days=1)
        before = timezone.now() - timedelta(hours=2)

        mrs = MatchRequest.objects.filter(
            creation__gte=since,
            creation__lte=before,
            retries__lte=3
        ).exclude(
            Q(status=MatchRequest.SUBMITTED) |
            Q(status=MatchRequest.COMPLETE)
        )
        for mr in mrs:
            mr.retries = mr.retries + 1
            mr.save()
            mr.status = MatchRequest.SUBMITTED


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
        cmp = CreateMatchParse()
        cmp.s(api_context=c).delay()

    def mark_finding(self, request):
        request.status = MatchRequest.FINDING_MATCH
        request.save()


class CreateMatchParse(Task):

    def run(self, api_context):

        match_id = api_context.match_id
        match_req = MatchRequest.objects.get(match_id=match_id)

        if match_req:
            rich_match_data = self.get_rich_data(match_id)

            if rich_match_data:
                logging.info('Got url for {0}'.format(match_id))
                self.make_match(rich_match_data, match_id, match_req)
                replay_url = Match.objects.get(steam_id=match_id).replay_url
                self._save_url(replay_url, match_req)
                self.java_parse_message(replay_url, match_id)
            else:
                logging.info('Did not get data for {0}'.format(match_id))
        else:
            raise Exception(
                "We don't have the match request we expected: {0}".format(
                    match_id
                )
            )

    def make_match(self, raw_data, match_id, match_req):
        """
        Because valve's data format is inconsistent, we need to munge things
        to make the normal functions work, then call the internals of that
        task.  This could be a mixin I guess.
        """

        # Unwrap the data
        dataset = raw_data['match']

        for player in dataset['players']:
            player['xp_per_min'] = player['XP_per_min']

        if dataset['match_outcome'] == 2:
            dataset['radiant_win'] = True
        elif dataset['match_outcome'] == 3:
            dataset['radiant_win'] = False
        else:
            raise ValueError(
                'what is this match outcome {0} for match {1}'.format(
                    dataset['match_outcome'],
                    match_id
                )
            )

        dataset['start_time'] = dataset['startTime']
        dataset['match_id'] = raw_data['id']
        dataset['tower_status_radiant'] = dataset['tower_status'][0]
        dataset['tower_status_dire'] = dataset['tower_status'][1]
        dataset['barracks_status_radiant'] = dataset[
            'barracks_status'
        ][0]
        dataset['barracks_status_dire'] = dataset['barracks_status'][1]

        c = ApiContext()
        c.match_id = match_id
        # TECHDEBT: calling the internals of a specific other class.
        # Could it be a mixin?  Probably.  I don't care right now.
        UpdateMatch().update_match(c, dataset, 200, "")

        match_req.status = MatchRequest.MATCH_FOUND
        match_req.save()

    def get_rich_data(self, match_id):
        logging.info('Getting the url for {0}'.format(match_id))
        return ReplayUrlBackend.objects.get_replay_url(match_id)

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

        logger.info('Draining')
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

        def drain(queue_name):

            method_frame, header_frame, body = channel.basic_get(queue_name)
            if not method_frame:
                return None
            else:
                json_data = json.loads(body)
                self.bookkeep(json_data)
                channel.basic_ack(method_frame.delivery_tag)

            return None

        while time.time() - start < 2:
            drain(queue_name)

        channel.cancel()
        channel.close()
        connection.close()

    def bookkeep(self, json_data):
        match_id = json_data['match_id']
        msg = json_data['msg']
        mr = MatchRequest.objects.get_or_create(match_id=match_id)[0]
        logger.info("Got {0} for M#{1}".format(msg, match_id))
        if msg == "done":
            mr.status = MatchRequest.COMPLETE
            mr.save()

            match = Match.objects.filter(steam_id=match_id)
            match.update(parsed_with=settings.PARSER_VERSION)
            logger.info('Parse Success!')

        elif msg == "not_found":
            mr.status = MatchRequest.REPLAY_NOT_AVAILABLE
            mr.save()
            logger.warning('Replay not available for {0}'.format(match_id))

        elif msg == "unknown_error":
            mr.status = MatchRequest.ERROR
            mr.save()
            logger.error('Mysterious error for {0}'.format(match_id))

        else:
            logger.error('What the hell happened for {0}?'.format(match_id))
            mr.status = MatchRequest.ERROR
            mr.save()
