from django.core.management.base import BaseCommand
from matches.management.tasks.valve_api_calls import (
    UpdateLeagueGames,
)


class Command(BaseCommand):

    def handle(self, *args, **options):
        UpdateLeagueGames().delay()
