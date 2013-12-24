from django.core.management.base import BaseCommand
from matches.management.tasks.valve_api_calls import RefreshUpdatePlayerPersonas, \
    RefreshPlayerMatchDetail, ApiContext, AcquireHeroSkillData
from heroes.models import Hero
class Command(BaseCommand):

    def handle(self, *args, **options):


        c = ApiContext()
        RefreshUpdatePlayerPersonas().delay(api_context=c)

        """
        heroes = Hero.objects.all()
        for hero in heroes:
            c = ApiContext()
            c.matches_requested = 1
            c.matches_desired = 1
            c.hero_id = hero.steam_id
            ahsd = AcquireHeroSkillData()
            ahsd.delay(api_context=c)
        """
        c = ApiContext()
        RefreshPlayerMatchDetail().delay(api_context=c)
