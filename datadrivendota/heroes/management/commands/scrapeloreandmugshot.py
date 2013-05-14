from urllib2 import urlopen
import urllib
from re import compile, MULTILINE

from django.utils.text import slugify
from django.core.management.base import BaseCommand
from django.core.files import File

from heroes.models import Hero


class Command(BaseCommand):

    def handle(self, *args, **options):

        prefix = "http://www.dota2wiki.com"
        all_heroes = Hero.objects.all()
        for h in all_heroes:

        # the first bit per API FAQ specs
            url = 'http://media.steampowered.com/apps/dota2/images/heroes/%s_full.png' % h.internal_name[14:]
            imgdata = urllib.urlretrieve(url)
            filename = slugify(h.name)+'_full.png'
            h.mugshot.save(filename, File(open(imgdata[0])))

            url = 'http://media.steampowered.com/apps/dota2/images/heroes/%s_sb.png' % h.internal_name[14:]
            imgdata = urllib.urlretrieve(url)
            filename = slugify(h.name)+'_thumb.png'
            h.thumbshot.save(filename, File(open(imgdata[0])))

            #Lore section
            undername = h.name.replace(" ", "_")
            herourl = prefix+"/wiki/"+undername
            html = urlopen(herourl).read()
            regex = compile(r"<td> <i>(?P<Lore>[^$]*?)</i", MULTILINE)
            r = regex.search(html)
            if r is not None:
                lore = r.groupdict()['Lore']
                lore = lore.replace("<p>", "\n")
                lore = lore.replace("<br />", " ")
                h.lore = lore
            else:
                print h.name+" has no lore!"

            h.save()
            print h.name
