from django.core.management.base import BaseCommand
from datadrivendota.management.tasks import ApiContext
from players.management.tasks import MirrorClientPersonas,


class Command(BaseCommand):

    def handle(self, *args, **options):

        c = ApiContext()
        MirrorClientPersonas().delay(api_context=c)
