from django.core.mail import send_mail
from uuid import uuid4
def safen(str):
    return str.replace('-',' ').replace('_',' ').title()

def error_email(subject, content):
    send_mail(subject,content,'datadrivendota@gmail.com',
        ['datadrivendota@gmail.com'],fail_silently=False)


###Auth Pipeline Stuff
def pipeline_test(backend, details, response, social_user, uid, user, *args, **kwargs):
    print backend, details, response, social_user, uid, user, args, kwargs
    return None

def request_to_player(request):
    user_id = request.user.social_auth.filter(provider='steam')[0].extra_data['steamid']
    user_id_32 = int(user_id) % settings.ADDER_32_BIT
    player = Player.objects.get(steam_id=user_id_32)
    return player
