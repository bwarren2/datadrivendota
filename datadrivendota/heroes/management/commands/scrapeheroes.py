import json
import requests

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from datadrivendota.settings.base import STEAM_API_KEY
from heroes.models import Hero


class Command(BaseCommand):

    def handle(self, *args, **options):

        param_dict = {'key': STEAM_API_KEY, 'language': 'en_us'}

        url = "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/"
        print "URL: {0}".format(url)
        data = json.loads(requests.get(url, params=param_dict))

        for row in data['result']['heroes']:
            print(row)
            try:
                hero = Hero.objects.get(steam_id=row['id'])
                hero.name = row['localized_name']
                hero.internal_name = row['name']
                hero.machine_name = slugify(row['localized_name'])
                hero.steam_id = row['id']
                hero.save()

            except Hero.DoesNotExist:
                hero = Hero(name=row['localized_name'],
                            internal_name=row['name'],
                            machine_name=slugify(row['localized_name']),
                            steam_id=row['id'])
                hero.name = row['localized_name']
                hero.internal_name = row['name']
                hero.machine_name = slugify(row['localized_name'])
                hero.steam_id = row['id']
                hero.save()
            self.stdout.write(row['localized_name'])
