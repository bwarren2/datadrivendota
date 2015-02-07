from django.core.management.base import BaseCommand
from datadrivendota.management.tasks import ApiContext
from heroes.management.tasks import MirrorHeroSkillData
from heroes.models import Hero
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
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
        if match_count <= 0:
            raise Exception("How many matches per hero? (Use --match-count)")
        heroes = Hero.objects.all()
        for hero in heroes:
            c = ApiContext()
            c.matches_requested = match_count
            c.matches_desired = match_count
            c.hero_id = hero.steam_id
            ahsd = MirrorHeroSkillData()
            ahsd.delay(api_context=c)
