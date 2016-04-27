from __future__ import unicode_literals

from datetime import timedelta
import logging

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

    def get_replay_url(self, match_id):
        # Constants:
        MATCH_ID = 'match_id'
        retry_erorrs = ('notready', 'timeout')
        fail_errors = ('invalid',)
        cooldown_errors = (
            # requests.exceptions.HTTPError,
            # RateLimitError,
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
            logger.info(replay_url.url, params)
            resp = requests.get(
                replay_url.url,
                params,
            )
            logger.info(resp)
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
                    do_not_use_before=now + timedelta(hours=24),
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
    objects = ReplayUrlBackendQuerySet.as_manager()

    url = models.URLField()
    do_not_use_before = models.DateTimeField(null=True)
