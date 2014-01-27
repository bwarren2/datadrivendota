from django.core.management.base import BaseCommand
from optparse import make_option
from players.models import PermissionCode


class Command(BaseCommand):

    option_list = BaseCommand.option_list+(
            make_option('--email',
                        action='store',
                        dest='email',
                        help='Who is getting the invite code?',),
            make_option('--level',
                        action='store',
                        dest='privilege_level',
                        help='Can they look, or touch?',),
    )

    def handle(self, *args, **options):
        email = options['email']
        privilege_level = options['privilege_level']


        if email is None:
            raise Exception("I need to have an email to send to. (Use --email)")

        if privilege_level.lower()=='look':
            pcode = PermissionCode.objects.create(upgrade_type=PermissionCode.LOOK)
        elif privilege_level.lower()=='touch':
            pcode = PermissionCode.objects.create(upgrade_type=PermissionCode.TOUCH)
        else:
            raise Exception("--level must be 'look' or 'touch', not {0}".format(privilege_level))

        pcode.send_to(email)
