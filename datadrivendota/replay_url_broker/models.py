from __future__ import unicode_literals

import sys, traceback
from datetime import timedelta
import logging
from requests.exceptions import ConnectionError

import requests
from django.db import models
from django.utils import timezone

from django.db.models import Q

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class ReplayUrlBackendQuerySet(models.QuerySet):
    def active_urls(self):
        now = timezone.now()
        return self.filter(
            Q(do_not_use_before__lte=now) |
            Q(do_not_use_before=None)
        )

    def timeout(self, delta, replay_url):
        now = timezone.now()
        self.filter(
            pk=replay_url.id,
        ).update(
            do_not_use_before=now + delta,
        )

    def get_replay_url(self, match_id):
        # Constants:
        MATCH_ID = 'match_id'
        retry_errors = ('notready',)    # Service not up.
        fail_errors = ('invalid',)      # That match ID is no good.
        fatal_errors = ('timeout', )    # Valve not responding.
        cooldown_errors = (
            requests.exceptions.HTTPError,
            RateLimitError,
            ConnectionError,
        )

        # We go through all active URLs, and try to get the replay URL for the
        # match_id from one of them. We expect to get it from the first, or
        # failing that, the second, so this loop should usually be short.
        #
        # If we get it, we return early.
        #
        # If we don't get it, we mark that URL for cooldown and try the next.
        active_urls = self.active_urls()
        if not active_urls:
            logger.warn(
                'No active replay URLs, things will fail for bad reasons'
            )
        for replay_url in active_urls:
            logger.info(
                'Hitting {0} with {1}'.format(replay_url.url, match_id)
            )
            params = {
                MATCH_ID: match_id,
            }
            try:
                resp = requests.get(
                    replay_url.url,
                    params,
                )

                logger.info(
                    "Got {0} from {1} with {2}".format(
                        resp, replay_url.url, params
                    )
                )

                # Process:
                resp.raise_for_status()
                logger.info(resp.content)
                resp_json = resp.json()

                error_code = resp_json.get('error')

                if error_code in fail_errors:
                    # We wanted an int, you passed us parakeets
                    return None
                if error_code in retry_errors:
                    self.timeout(timedelta(seconds=30), replay_url)
                if error_code in fatal_errors:
                    # TODO make this route to a shorter cooldown?
                    raise RateLimitError

                return resp_json.get('replay_url')
            except cooldown_errors as exc:
                logger.error(
                    "Exception {0} on urlbackend: {1}".format(
                        exc,
                        traceback.print_exc()
                    )
                )
                # mark this URL as bad as of now:
                self.timeout(timedelta(hours=24), replay_url)

            except ValueError as e:
                logger.error(
                    "Exception: {0} for content: {1}".format(
                        type(e).__name__,
                        resp.content
                    )
                )
        # Guess we didn't find it. Let's explicitly return:
        return None


class ReplayUrlBackend(models.Model):
    objects = ReplayUrlBackendQuerySet.as_manager()

    url = models.URLField()
    do_not_use_before = models.DateTimeField(null=True)

    def __unicode__(self):
        fragment = self.url[8:self.url.find('.herokuapp')]
        usable = (
            self.do_not_use_before is None or
            timezone.now() > self.do_not_use_before
        )
        if usable:
            useable = 'usable'
        else:
            useable = 'OUT OF SERVICE'

        return "{0}, {1} ({2})".format(
            fragment,
            useable,
            self.do_not_use_before.strftime("%m-%d %H:%M:%S")
        )
