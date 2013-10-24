from django.core.management.base import BaseCommand
from matches.management.tasks.valve_api_calls import RefreshUpdatePlayerPersonas, RefreshPlayerMatchDetail, ApiContext
class Command(BaseCommand):

    def handle(self, *args, **options):


        c = ApiContext()
        RefreshUpdatePlayerPersonas().delay(api_context=c)
        c = ApiContext()
        RefreshPlayerMatchDetail().delay(api_context=c)

