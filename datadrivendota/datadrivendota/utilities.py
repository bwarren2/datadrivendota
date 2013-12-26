from django.core.mail import send_mail
from django.conf import settings
from players.models import Player
def safen(str):
    return str.replace('-',' ').replace('_',' ').title()

def error_email(subject, content):
    send_mail(subject,content,'datadrivendota@gmail.com',
        ['datadrivendota@gmail.com'],fail_silently=False)


###Auth Pipeline Stuff
def create_player(strategy, response, *args, **kwargs):
    steam_64_id = kwargs['uid']
    p = Player.objects.get_or_create(steam_id=steam_64_id)
    return {'player_created':p[1]}
