import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files import File

from heroes.models import Role


class Command(BaseCommand):

    """
    Add pips to the roles.

    You should not need to do this often,
    but it is required in restoring from 0.
    """

    def handle(self, *args, **options):

        all_roles = Role.objects.exclude(name='')
        # matching_dict = {
        #     'Nuker': u'32px-Pip_ganker.png',
        #     'Disabler': u'32px-Pip_disabler.png',
        #     'Escape': u'32px-Pip_tank.png',
        #     'Initiator': u'32px-Pip_initiator.png',
        #     'Support': u'32px-Pip_roamer.png',
        #     'Jungler': u'32px-Pip_jungler.png',
        #     'Pusher': u'32px-Pip_pusher.png',
        #     'Durable': u'32px-Pip_tank.png',
        #     'LaneSupport': u'32px-Pip_babysitter.png',
        #     'Carry': u'32px-Pip_carry.png',
        # }

        matching_dict = {
            'Nuker': u'ganker.png',
            'Disabler': u'disabler.png',
            'Initiator': u'initiator.png',
            'Support': u'roamer.png',
            'Jungler': u'jungler.png',
            'Pusher': u'pusher.png',
            'Escape': u'durable.png',
            'Durable': u'durable.png',
            'LaneSupport': u'lanesupport.png',
            'Carry': u'carry.png',
        }
        for role in all_roles:

            url = (
                'https://s3.amazonaws.com/datadrivendota/images/pips/{suffix}'.format(
                    suffix=matching_dict[role.name])
            )
            print url
            resp = requests.get(url)

            if resp.status_code == 200:
                buff = BytesIO(resp.content)
                _ = buff.seek(0)  # Avoid printing random numbers.
                _ = _
                filename = matching_dict[role.name]
                role.thumbshot.save(filename, File(buff))

            else:
                role.thumbshot = None
                print "No thumbshot for %s!" % (role.name)

            role.save()
