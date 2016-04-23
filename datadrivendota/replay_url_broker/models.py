from __future__ import unicode_literals

from datetime import timedelta
import logging

import requests
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class RateLimitError(Exception):
    pass


class ReplayUrlBackendQuerySet(models.QuerySet):
    def active_urls(self, COOLDOWN=timedelta(hours=24)):
        now = timezone.now()
        return self.filter(
            last_bad_time__lt=now - COOLDOWN,
        )

    def get_replay_url(self, match_id):
        # Constants:
        retry_erorrs = ('notready', 'timeout')
        fail_errors = ('invalid',)
        cooldown_errors = (
            requests.exceptions.HTTPError,
            RateLimitError,
        )

        # We go through all active URLs, and try to get the replay URL for the
        # match_id from one of them. We expect to get it from the first, or
        # failing that, the second, so this loop should usually be short.
        #
        # If we get it, we return early.
        #
        # If we don't get it, we mark that URL for cooldown and try the next.
        for replay_url in self.active_urls():
            logger.info(
                'Hitting {0} with {1}'.format(replay_url.url, match_id)
            )
            resp = requests.get(
                replay_url.url,
                params={
                    self.MATCH_ID: match_id,
                },
            )
            try:
                # Process:
                resp.raise_for_status()
                logger.info(resp.content)
                resp_json = resp.json()

                error_code = resp_json.get('error')
                if error_code in fail_errors:
                    raise RateLimitError
                if error_code in retry_erorrs:
                    # TODO make this route to a shorter cooldown?
                    raise RateLimitError
                return resp_json.get('replay_url')
            except cooldown_errors:
                # mark this URL as bad as of now:
                now = timezone.now()
                self.filter(
                    pk=replay_url.id,
                ).update(
                    last_bad_time=now,
                )
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
    MATCH_ID = 'match_id'
    COOLDOWN = timedelta(hours=24)

    objects = ReplayUrlBackendQuerySet.as_manager()

    url = models.URLField()
    last_bad_time = models.DateTimeField(null=True)
