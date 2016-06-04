import functools as ft
import logging
import gzip
import time
import pika
import sys
import json
import requests
from io import BytesIO
from collections import Counter
from contextlib import closing
from datetime import timedelta
from retrying import retry

from celery import Task, chain

from django.core.files import File
from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from utils import gzip_str, gunzip_str
from parserpipe.models import MatchRequest
from datadrivendota.management.tasks import ValveApiCall, ApiContext
from datadrivendota.s3utils import ParseS3BotoStorage
from matches.management.tasks import UpdateMatch
from matches.models import Match, PlayerMatchSummary
from accounts.models import get_customer_player_ids
from leagues.models import League
from replay_url_broker.models import ReplayUrlBackend

from .combat_log_filters import combatlog_filter_map
from .state_log_filters import entitystate_filter_map

logger = logging.getLogger(__name__)


# This is tightly coupled to the S3WriterTaskMixin.
#  - It takes a single args tuple, and unpacks it inside the function.
#  - It assumpes the input buffers are BytesIO objects with a getvalue method.
# Sometimes boto raises S3ResponseError: 200 OK with an "internal error" msg.
# Retrying tries to hammer around the problem.
@retry(stop_max_delay=10000, wait_fixed=2000)
def upload_to_s3(args):
    # We have to take and unpack a tuple to play nicely with ThreadPool.map:
    input_buffer, filename = args
    with closing(ParseS3BotoStorage().open(filename, 'w')) as f:
        f.write(input_buffer.getvalue())


class S3WriterTaskMixin(object):
    def __init__(self, *args, **kwargs):
        ret = super(S3WriterTaskMixin, self).__init__(*args, **kwargs)
        self.upload_queue = []
        return ret

    def shard_filename(self, match_id, dataslice, facet, log_type):
        """
        Get the filename for shards on s3.

        Because we are effectively using s3 as a great big key-value store,
            we need a hashing fn.  This is it.

        :param match_id: steam_id for match
        :param dataslice: player_slot of {radiant/dire/diff}
        :param log_type: {combatlog/statelog/combatseries}
        :param facet: the name of a filter fn from that msg type
        :returns: formatted string
        """
        filename = '{0}_{1}_{2}_{3}_v{4}.json.gz'.format(
            match_id,
            dataslice,
            log_type,
            facet,
            settings.PARSER_VERSION
        )

        return filename

    def shard_url(self, match_id, dataslice, facet, log_type):
        return settings.SHARD_URL_BASE + self.shard_filename(
            match_id,
            dataslice,
            facet,
            log_type,
        )

    def save_msgstream(self, match_id, dataslice, msgs, facet, log_type):
        raw_bytes = BytesIO()
        gzip_wrapper = gzip.GzipFile(
            mode='wb',
            fileobj=raw_bytes,
        )
        json.dump(msgs, gzip_wrapper)

        filename = self.shard_filename(match_id, dataslice, facet, log_type)
        self.upload_queue.append((raw_bytes, filename))

    def finalize_write_to_s3(self):
        logger.info("Uploading {} files to S3".format(len(self.upload_queue)))

        logger.info("In particular, these:")
        for a, b in self.upload_queue:
            logger.info(b)

        logger.info("In particular, these:")
        map(upload_to_s3, self.upload_queue)
        self.upload_queue = []


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
    soft_time_limit = 120
    time_limit = 125

    def run(self, json_data):

        match_id = json_data['match_id']
        filename = json_data['filename']

        logger.info(json_data)
        logger.info('Handling {0}'.format(match_id))

        try:

            mr = MatchRequest.objects.get(match_id=match_id)

            if filename == 'notfound':
                mr.status = MatchRequest.REPLAY_NOT_AVAILABLE
                mr.save()

            else:
                logger.info('Merging {0} to request'.format(match_id))
                self.merge_to_request(mr, filename)

                logger.info('Merging {0} to match'.format(match_id))
                self.merge_to_match(mr, match_id)

                logger.info('Fanning out {0}'.format(match_id))
                self.fan_parsing(match_id)

        except MatchRequest.DoesNotExist:
            logger.error(
                'No matchrequest found for {0}'.format(match_id)
            )

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
        slices = Match.PLAYER_SLOTS

        chain(
            UpdatePmsReplays().s(match_id=match_id, data_slices=slices),
            UpdateParseEnd().s(match_id=match_id)
        ).delay()  # Queue for postprocessing


class UpdatePmsReplays(S3WriterTaskMixin, Task):
    ignore_result = False
    soft_time_limit = 180
    time_limit = 185

    def run(self, match_id, data_slices):

        logger.info('Doing prep for {0}'.format(match_id))
        match = Match.objects.get(steam_id=match_id)

        replay = json.loads(gunzip_str(match.compressed_replay.read()))

        offset = self.get_offset(replay, match_id)
        replay = self.convert_times(replay, offset)
        replay = self.convert_stringtables(replay)
        logger.info('Prep done for {0}'.format(match_id))
        return_pmses = []

        for data_slice in data_slices:
            logger.info(
                'Sharding replay for {0} {1}'.format(
                    match_id, data_slice
                )
            )
            pms_qs = PlayerMatchSummary.objects.filter(
                match__steam_id=match_id,
                player_slot=data_slice
            ).select_related('hero')
            pms = pms_qs[0]

            self.shard(replay, pms, offset, match.steam_id)
            # TODO something like this,
            # and change save_msgstream to just build
            # an in-memory buffer in this task?
            return_pmses.append(pms.id)

        self.finalize_write_to_s3()
        return return_pmses

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

        logging.info(
            'Working on this pms: {0}'.format(
                pms
            )
        )

        enemies = pms.enemies
        allies = pms.allies
        logging.info(
            "Sharding for {0} in match {1}".format(
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

        logging.info('State list size: {0}'.format(len(state_list)))

        # Get the timing information to make the combat timeseries match states
        min_time = min(x['tick_time'] for x in state_list)
        max_time = max(x['tick_time'] for x in state_list)
        timeseries_log = self.timeseries_combat(
            pms_combat, min_time, max_time, offset
        )
        self.save_timeseries(match_id, pms, timeseries_log)

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

            data = filter_fn(replay['es'], pms, enemies, allies)
            if field == 'item_buys':
                self.save_msgstream(
                    match_id, pms.player_slot, data, field, 'combatlog'
                )
            else:
                pass
                # We are not actually using this data right now.
                #  We can circle back later on this if there is interest.
            pms_combat[field] = data

        return pms_combat

    def timeseries_combat(self, pms_combat, min_time, max_time, offset):
        """
        Change combat log events into sum of values or msg-count time series.
        """

        combat_timeseries = {}
        for field, data in pms_combat.iteritems():
            indicies = {n: 0 for n in range(min_time, max_time + 1)}

            # Sum up the messages occurring at the same time
            for msg in data:

                # How are there combatmessages without state messages?
                #  Discarding for now.

                if msg['time'] in indicies:
                    indicies[msg['time']] += msg.get('value', 1)
                else:
                    logging.error("""
                        For {0}, got msg time {1} not between {2} - {3}
                    """.format(
                            field, msg['time'], min_time, max_time
                        )
                    )
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
        """ We are rolling this into one file as a speed hack. """

        merged_data = [
            self.merge_combatseries_dicts(idx, timeseries_log)
            for idx in range(0, len(timeseries_log.values()[0]))
        ]
        logging.info('Saving truncated combatseries')
        self.save_msgstream(
            match_id, pms.player_slot, merged_data, 'allseries', 'combatseries'
        )

    def merge_combatseries_dicts(self, idx, datadict):
        relevant_dicts = [v[idx] for v in datadict.values()]
        return ft.reduce(
            lambda a, b: dict(a, **b),
            relevant_dicts,
            {}
        )


class UpdateParseEnd(S3WriterTaskMixin, Task):
    soft_time_limit = 600
    time_limit = 605

    def run(self, finished_shards, match_id):
        #  Expects a bunch of pms ids on all success, some falsy on any failure

        if all(finished_shards):

            for ct, field in enumerate(entitystate_filter_map.keys()):
                # these are not summable
                if field in [
                    'items', 'position', 'x_position', 'y_position'
                ]:
                    continue

                logger.info(
                    'Doing M#{0}, {1}, {2}.  {3} done.'.format(
                        match_id, field, 'statelog', ct
                    )
                )

                self.aggregate_shards(match_id, field, 'statelog')

            self.aggregate_shards(match_id, 'allseries', 'combatseries')

            self.bookkeep(match_id)
            # TODO something like this, and change save_msgstream to just build
            # an in-memory buffer in this task?
            self.finalize_write_to_s3()
        else:
            raise ValueError("Something failed in the parse chord")

    def bookkeep(self, match_id):
        mr = MatchRequest.objects.get_or_create(match_id=match_id)[0]
        mr.status = MatchRequest.COMPLETE
        mr.save()

        match = Match.objects.filter(steam_id=match_id)
        match.update(parsed_with=settings.PARSER_VERSION)
        logger.info('Parse Success!')

    def aggregate_shards(self, match_id, field, logtype):

        radiant = self.get_files(
            match_id, Match.RADIANT_SLOTS, field, logtype
        )
        dire = self.get_files(match_id, Match.DIRE_SLOTS, field, logtype)

        radiant_sum = self.rollup_dataseries(radiant, field,  'sum')
        dire_sum = self.rollup_dataseries(dire, field, 'sum')
        diff = self.rollup_dataseries([radiant_sum, dire_sum], field, 'diff')

        self.save_msgstream(match_id, 'radiant', radiant_sum, field, logtype)
        self.save_msgstream(match_id, 'dire', dire_sum, field, logtype)
        self.save_msgstream(match_id, 'diff', diff, field, logtype)

    def get_files(self, match_id, dataslices, field, logtype):
        """
        Get the files for shards on s3.

        :param match_id: steam_id for match
        :param dataslices: a list of player_slots
        :param field: the name of a filter fn from that msg type
        :param log_type: {combatlog/statelog/combatseries}
        :returns: a list of lists of dicts, pulled from s3
        """
        return_lst = []
        for x in dataslices:
            url = self.shard_url(match_id, x, field, logtype)
            return_lst.append(
                requests.get(url).json()
            )

        return return_lst

    def rollup_sum_allstate(self, data_keys, data_dicts):
        return_lst = []
        bad_keys = [
            'offset_time',
            'x',
            'y',
            'item_0',
            'item_1',
            'item_2',
            'item_3',
            'item_4',
            'item_5',
            'health_pct',
            'mana_pct',
        ]
        for x in data_keys:
            struct = {
                'offset_time': data_dicts[0][x]['offset_time'],
            }
            keys = (k for k in data_dicts[0][x].keys() if k not in bad_keys)
            for key in keys:
                struct[key] = sum([subdict[x][key] for subdict in data_dicts])

            try:
                health_pct = sum(
                    [subdict[x]['health'] for subdict in data_dicts]
                ) / sum(
                    [subdict[x]['max_health'] for subdict in data_dicts]
                )
                mana_pct = sum(
                    [subdict[x]['mana'] for subdict in data_dicts]
                ) / sum(
                    [subdict[x]['max_mana'] for subdict in data_dicts]
                )
                struct['health_pct'] = health_pct
                struct['mana_pct'] = mana_pct
            except KeyError:
                # Health key not present, probably in combatseries.
                pass

            return_lst.append(struct)

        return return_lst

    def rollup_dataseries(self, data, field, operation):
        """
        Reduce the lists of files into one series with continuous time keys.

        :param match_id: a list of lists of objects.
        :param operation: sum or diff.
        """

        data_dicts = self.rehash(data, field)
        data_keys = self.extract_keys(data_dicts)

        if operation == 'sum':
            if field == 'allstate' or field == 'allseries':
                return self.rollup_sum_allstate(data_keys, data_dicts)
            else:
                return [
                    {
                        'offset_time': x,
                        field: sum([subdict[x] for subdict in data_dicts])
                    }
                    for x in data_keys
                ]
        elif operation == 'diff':
            if len(data) != 2:
                raise ValueError(
                    'Taking dicts of more than 2 series undefined.'
                )
            else:
                if field == 'allstate' or field == 'allseries':
                    return_lst = []

                    for time_idx in data_keys:
                        diff_dict = {
                            'offset_time': time_idx,
                        }
                        for attr in data_dicts[0][time_idx].keys():
                            if attr in data_dicts[1][time_idx].keys() and attr != 'offset_time':
                                diff_dict[attr] = (
                                    data_dicts[0][time_idx][attr] -
                                    data_dicts[1][time_idx][attr]
                                )
                        return_lst.append(diff_dict)
                    return return_lst

                else:
                    return [
                        {
                            'offset_time': x,
                            field: data_dicts[0][x] - data_dicts[1][x]
                        }
                        for x in data_keys
                    ]
        else:
            raise ValueError('What is this operation? {0}'.format(operation))

    def rehash(self, data, field):
        if field != 'allstate' and field != 'allseries':
            return [
                {x['offset_time']: x[field] for x in dataseries}
                for dataseries in data
            ]
        else:
            return [
                {x['offset_time']: x for x in dataseries}
                for dataseries in data
            ]

    def extract_keys(self, data):
        keys_list = [
            x
            for dataseries in data
            for x in dataseries.keys()
        ]
        counts = Counter(keys_list)
        datalength = len(data)
        eligible_keys = [x for x, y in counts.iteritems() if y == datalength]

        if len(eligible_keys) != max(eligible_keys) - min(eligible_keys) + 1:
            raise ValueError('Why do we have an noncontinuous dataseries?')

        return sorted(eligible_keys)


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
