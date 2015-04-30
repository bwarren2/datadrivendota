from uuid import uuid4
from urllib2 import urlopen, HTTPError
from django.utils.text import slugify
from django.core.management.base import BaseCommand
from django.core.files import File

from heroes.models import Role


class Command(BaseCommand):
    """
    Add pips to the roles.  You should not need to do this often,
    but it is required in restoring from 0.
    """
    def handle(self, *args, **options):

        all_roles = Role.objects.exclude(name='')
        matchingDict = {
            'Nuker': u'32px-Pip_ganker.png',
            'Disabler': u'32px-Pip_disabler.png',
            'Escape': u'32px-Pip_tank.png',
            'Initiator': u'32px-Pip_initiator.png',
            'Support': u'32px-Pip_roamer.png',
            'Jungler': u'32px-Pip_jungler.png',
            'Pusher': u'32px-Pip_pusher.png',
            'Durable': u'32px-Pip_tank.png',
            'LaneSupport': u'32px-Pip_babysitter.png',
            'Carry': u'32px-Pip_carry.png',
        }
        for role in all_roles:

            url = (
                'https://s3.amazonaws.com/datadrivendota/pips/{suffix}'.format(
                    suffix=matchingDict[role.name])
            )
            try:
                imgdata = urlopen(url)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())
                filename = matchingDict[role.name]
                role.thumbshot.save(filename, File(open(f.name)))
            except HTTPError, err:
                role.thumbshot = None
                print "No thumbshot for %s!  Error %s" % (role.name, err)

            role.save()
