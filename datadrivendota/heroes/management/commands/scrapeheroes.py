import requests

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from datadrivendota.settings.base import STEAM_API_KEY
from heroes.models import Hero


class Command(BaseCommand):

    def handle(self, *args, **options):

        data = self.get_heroes()
        self.create_heroes(data)

    def get_heroes(self):
        """
        Hit the valve API for the current hero list.
        """
        param_dict = {'key': STEAM_API_KEY, 'language': 'en_us'}
        url = "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/"
        r = requests.get(url, params=param_dict)

        return r.json()

    def create_heroes(self, data):
        """
        Turn each row in the data into a hero
        """
        for row in data['result']['heroes']:

            hero, created = Hero.objects.update_or_create(
                steam_id=row['id'],
                defaults={
                    'name': row['localized_name'],
                    'internal_name': row['name'],
                    'machine_name': slugify(row['localized_name']),
                    'steam_id': row['id'],
                })
