from uuid import uuid4
from urllib2 import urlopen, HTTPError
from re import compile, MULTILINE
from django.utils.text import slugify
from django.core.management.base import BaseCommand
from django.core.files import File
from BeautifulSoup import BeautifulSoup

from heroes.models import Hero


class Command(BaseCommand):

    def handle(self, *args, **options):

        prefix = "http://www.dota2.com/hero/"
        all_heroes = Hero.objects.exclude(name='')
        for h in all_heroes:

        # the first bit per API FAQ specs
            url = 'http://media.steampowered.com/apps/dota2/images/heroes/%s_full.png' % h.internal_name[14:]
            try:
                imgdata = urlopen(url)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())
                filename = slugify(h.name)+'_full.png'
                h.mugshot.save(filename, File(open(f.name)))
            except HTTPError, err:
                h.mugshot = None
                print "No mugshot for %s!  Error %s" % (h.name, err)

            url = 'http://media.steampowered.com/apps/dota2/images/heroes/%s_sb.png' % h.internal_name[14:]
            try:
                imgdata = urlopen(url)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())
                filename = slugify(h.name)+'_thumb.png'
                h.thumbshot.save(filename, File(open(f.name)))
            except HTTPError, err:
                h.thumbshot = None
                print "No thumbshot for %s!  Error %s" % (h.name, err)

            #Lore section
            undername = h.name.replace(" ", "_")
            undername = undername.replace("'", "")
            herourl = prefix+undername
            try:

                html = urlopen(herourl).read()
                bs = BeautifulSoup(html)
                lore = bs.find("div",{'id':'bioInner'}).getText(separator=u' ')
                h.lore = lore
            except HTTPError, err:
                print "No lore for %s!  Error %s" % (h.name, err)
            except AttributeError, err:
                print "{hero} has no lore {err} {url}".format(hero=h.name, err=err,url=herourl)

            h.save()
            print h.name
