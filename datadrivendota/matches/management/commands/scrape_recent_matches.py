from django.core.management.base import BaseCommand
from matches.management.tasks.valve_api_calls import (
    RefreshPlayerMatchDetail,
    ApiContext
)
from optparse import make_option


class Command(BaseCommand):

    option_list = BaseCommand.option_list+(
        make_option(
            '--match-count',
            action='store',
            dest='match_count',
            help='How many matches per hero?'
        ),
    )

    def handle(self, *args, **options):
        match_count = options['match_count']
        c = ApiContext()
        if match_count > 0:
            c.matches_desired = match_count

        RefreshPlayerMatchDetail().delay(api_context=c)
