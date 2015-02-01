from django.core.management.base import BaseCommand
from leagues.management.tasks import UpdateLeagueGames


class Command(BaseCommand):

    def handle(self, *args, **options):
        UpdateLeagueGames().delay()
