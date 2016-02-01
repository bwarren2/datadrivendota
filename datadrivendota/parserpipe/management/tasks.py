import logging
import time
import pika
import sys
import json
import requests
from io import BytesIO

from celery import Task, chain, chord

from django.core.files import File
from django.conf import settings
from django.db.models import Q

from utils import gzip_str, gunzip_str
from utils.file_management import s3_parse
from parserpipe.models import MatchRequest
from datadrivendota.management.tasks import ValveApiCall, ApiContext
from matches.management.tasks import UpdateMatch
from matches.models import Match, PlayerMatchSummary


from .combat_log_filters import combatlog_filter_map
from .state_log_filters import entitystate_filter_map

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
                MergeMatchRequestReplay().delay(json_data=json.loads(body))
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

        logger.info(json_data)
        logger.info('Merging {0}'.format(match_id))

        mr = MatchRequest.objects.get(match_id=match_id)
        logger.info('Merging {0} to request'.format(match_id))
        self.merge_to_request(mr, filename)

        logger.info('Merging {0} to match'.format(match_id))
        self.merge_to_match(mr, match_id)

        logger.info('Fanning out {0}'.format(match_id))
        self.fan_parsing(match_id)

    def merge_to_match(self, mr, match_id):
        match = Match.objects.get(steam_id=match_id)
        mr = MatchRequest.objects.get(match_id=match_id)
        url = mr.file_url
        logging.info("Got file url {0}".format(url))
        try:
            r = requests.get(url)
            if r.status_code == 200:
                holder = BytesIO(r.content)
                holder.seek(0)
                filename = "{0}_parse.json".format(match_id)
                match.replay.save(filename, File(holder))

                holder = BytesIO(gzip_str(r.content))
                holder.seek(0)
                filename = "{0}_parse.json.gz".format(match_id)
                logging.info(
                    'Saved compressed replay raw parse {0}'.format(
                        filename
                    )
                )
                match.compressed_replay.save(filename, File(holder))

            else:
                raise ValueError(
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

    def fan_parsing(self, match_id):
        callback = UpdateParseEnd().s(match_id=match_id)
        slices = Match.PLAYER_SLOTS

        header = [
            UpdatePmsReplays().s(match_id=match_id, data_slice=x)
            for x in slices
        ]
        chord(header)(callback)  # Queue for postprocessing


class UpdatePmsReplays(Task):
    ignore_result = False
    soft_time_limit = 180
    time_limit = 185

    def run(self, match_id, data_slice):
        logger.info('Sharding replay for {0} {1}'.format(match_id, data_slice))

        match = Match.objects.get(steam_id=match_id)

        replay = json.loads(gunzip_str(match.compressed_replay.read()))

        offset = self.get_offset(replay, match_id)
        replay = self.convert_times(replay, offset)
        replay = self.convert_stringtables(replay)

        if data_slice in Match.PLAYER_SLOTS:
            pms_qs = PlayerMatchSummary.objects.filter(
                match__steam_id=match_id,
                player_slot=data_slice
            ).select_related('hero')
            pms = pms_qs[0]

            self.shard(replay, pms, offset, match.steam_id)
            return pms.id

        else:
            raise ValueError('What is this dataslice? {0}'.format(data_slice))
            return None

    def convert_stringtables(self, replay):

        item_map = {
            msg['idx']: msg['value']
            for msg in replay['stl']
        }
        tags = ['item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5']

        for msg in replay['states']:
            for item_tag in tags:
                if item_tag in msg:
                    msg[item_tag] = item_map[msg[item_tag]]
                else:
                    msg[item_tag] = None

        return replay

    def convert_times(self, replay, offset):
        for msg in replay['es']:
            msg['offset_time'] = msg['time'] - offset
        for msg in replay['states']:
            msg['offset_time'] = msg['tick_time'] - offset
        return replay

    def get_offset(self, replay, match_id):
        states = [
            x for x in replay['es']
            if x['type'] == 'state' and x['key'] == 'PLAYING'
        ]
        try:
            offset = states[0]['time']
        except IndexError:
            offset = 0
            logger.error(
                'Failed to get an offset with match {0}'.format(match_id)
            )

        return offset

    def shard(self, replay, pms, offset, match_id):

        enemies = pms.enemies
        allies = pms.allies
        logging.info("Sharding for {0} in match {1}".format(
            pms.hero.name, pms.match.steam_id
            )
        )

        # Save event-oriented combatlog
        pms_combat = self.save_combat(pms, match_id, replay, enemies, allies)

        # Save timeseries-oriented statelog
        self.save_states(pms, match_id, replay)

        # Aggregate all the state info
        state_list = [
            msg for msg in
            replay['states'] if msg['hero_id'] == pms.hero.steam_id
        ]

        # Get the timing information to make the combat timeseries match states
        min_time = min(x['tick_time'] for x in state_list)
        max_time = max(x['tick_time'] for x in state_list)
        timeseries_log = self.timeseries_combat(
            pms_combat, min_time, max_time, offset
        )
        self.save_timeseries(match_id, pms, timeseries_log)

        all_data = {
            'states': state_list,
            'combat': pms_combat,
        }
        self.save_msgstream(match_id, pms.player_slot, all_data, 'all', 'both')

    def save_states(self, pms, match_id, replay):
        for field, filter_fn in entitystate_filter_map.iteritems():
            logging.info("Handling field {0} for {1} (M# {2})".format(
                field,
                pms.hero.name,
                pms.match.steam_id,
            ))
            data = filter_fn(replay['states'], pms)
            self.save_msgstream(
                match_id, pms.player_slot, data, field, 'statelog'
            )

    def save_combat(self, pms, match_id, replay, enemies, allies):
        pms_combat = {}

        for field, filter_fn in combatlog_filter_map.iteritems():
            logging.info("Handling field {0} for {1} (M# {2})".format(
                field,
                pms.hero.name,
                pms.match.steam_id,
            ))
            data = filter_fn(replay['es'], pms, enemies, allies)
            self.save_msgstream(
                match_id, pms.player_slot, data, field, 'combatlog'
            )
            pms_combat[field] = data

        return pms_combat

    def timeseries_combat(self, pms_combat, min_time, max_time, offset):
        """
        Change combat log events into sum of values or msg-count time series.
        """

        combat_timeseries = {}
        for field, data in pms_combat.iteritems():
            indicies = {n: 0 for n in range(min_time, max_time+1)}

            # Sum up the messages occurring at the same time
            for msg in data:
                indicies[msg['time']] += msg.get('value', 1)

            # Make them cumulative
            for idx in indicies.iterkeys():
                indicies[idx] += indicies.get(idx-1, 0)

            # Add in the timing info
            timeseries = [
                {
                    'time': idx,
                    'offset_time': idx - offset,
                    field: indicies[idx],
                } for idx in indicies.keys()
            ]

            combat_timeseries[field] = timeseries

        return combat_timeseries

    def save_timeseries(self, match_id, pms, timeseries_log):
        for field, data in timeseries_log.iteritems():
            self.save_msgstream(
                match_id, pms.player_slot, data, field, 'combatseries'
            )

    def save_msgstream(self, match_id, dataslice, msgs, facet, msgs_type):
        buff = BytesIO(json.dumps(msgs))
        buff.seek(0)

        filename = '{0}_{1}_{2}_{3}_v{4}.json.gz'.format(
            match_id,
            dataslice,
            msgs_type,
            facet,
            settings.PARSER_VERSION
        )
        logger.info("Saving {0}".format(filename))
        s3_parse(buff, filename)


class UpdateParseEnd(Task):

    def run(self, finished_shards, match_id):
        #  Expects a bunch of pms ids on all success, some falsy on any failure

        if all(finished_shards):

            mr = MatchRequest.objects.get(match_id=match_id)
            mr.status = MatchRequest.PARSED
            mr.save()

            pms_ids = finished_shards
            pmses = PlayerMatchSummary.objects.filter(id__in=pms_ids)
            pmses.update(parsed_with=settings.PARSER_VERSION)
            logger.info('Parse Success!')
        else:
            raise ValueError("Something failed in the parse chord")