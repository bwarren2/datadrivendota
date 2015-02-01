from django.core.management.base import BaseCommand
from players.management.tasks import MirrorClientMatches
from datadrivendota.management.tasks import ApiContext
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
        match_count = int(match_count)
        c = ApiContext()
        if match_count > 0:
            c.matches_desired = match_count

        MirrorClientMatches().delay(api_context=c)
