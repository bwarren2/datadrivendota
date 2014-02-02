from django.core.management.base import BaseCommand
from matches.management.tasks.valve_api_calls import RefreshUpdatePlayerPersonas, \
    RefreshPlayerMatchDetail, ApiContext, AcquireHeroSkillData
from heroes.models import Hero
class Command(BaseCommand):

    def handle(self, *args, **options):

        c = ApiContext()
        RefreshUpdatePlayerPersonas().delay(api_context=c)
