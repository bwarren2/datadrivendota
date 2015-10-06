import sys
from urllib2 import urlopen, HTTPError
from io import BytesIO
import requests

from django.utils.text import slugify
from django.core.management.base import BaseCommand
from django.core.files import File

from BeautifulSoup import BeautifulSoup

from heroes.models import Hero


class Command(BaseCommand):

    def handle(self, *args, **options):

        all_heroes = Hero.objects.exclude(name='')
        for h in all_heroes:

            self.add_images(h)
            self.add_lore(h)
            self.validate_visible(h)

    def add_images(self, hero):
        """
        Hit Valve APIs for pictures.

        This can be refactored for better testing, but not a high priority yet.
        """
        # Full-size images
        url = (
            'http://media.steampowered.com'
            '/apps/dota2/images/heroes/{0}_full.png'.format(
                hero.internal_name[14:]
            )
        )
        print(url)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                holder = BytesIO(r.content)
                _ = holder.seek(0)  # NOQA
                filename = slugify(hero.name) + '_full.png'
                hero.mugshot.save(filename, File(holder))
            else:
                print(
                    "No mugshot for {0}!  Error code {1}".format(
                        hero.name, r.status_code
                    )
                )

        except:
            err = sys.exc_info()[0]
            print("No mugshot for %s!  Error %s" % (hero.name, err))

        # Thumb-size images
        url = (
            'http://media.steampowered.com'
            '/apps/dota2/images/heroes/%s_sb.png' % hero.internal_name[14:]
        )
        print(url)
        try:
            r = requests.get(url)
            if r.status_code == 200:
                holder = BytesIO(r.content)
                _ = holder.seek(0)  # NOQA
                filename = slugify(hero.name) + '_thumb.png'
                hero.thumbshot.save(filename, File(holder))
            else:
                print(
                    "No mugshot for {0}!  Error code {1}".format(
                        hero.name, r.status_code
                    )
                )
        except:
            err = sys.exc_info()[0]
            print("No mugshot for %s!  Error %s" % (hero.name, err))

    def add_lore(self, hero):
        """
        Hit foreign APIs for lore.

        This can be refactored for better testing, but not a high priority yet.
        """
        undername = hero.name.replace(" ", "_")
        undername = undername.replace("'", "")
        herourl = "http://www.dota2.com/hero/" + undername
        try:
            html = urlopen(herourl).read()
            bs = BeautifulSoup(html)
            lore = bs.find(
                "div",
                {'id': 'bioInner'}
            ).getText(separator=u' ')
            hero.lore = lore

        except HTTPError as err:
            print("No lore for %s!  Error %s" % (hero.name, err))
        except AttributeError as err:
            print(
                "{hero} has no lore {err} {url}".format(
                    hero=hero.name,
                    err=err,
                    url=herourl
                )
            )

        hero.save()

    def validate_visible(self, hero):

        if hero.has_image:
            hero.visible = True
        else:
            hero.visible = False
        hero.save()
