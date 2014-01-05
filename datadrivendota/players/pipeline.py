from players.models import Player, UserProfile
from django.conf import settings
from django.contrib.auth.models import User

def create_player(strategy, details, response, *args, **kwargs):
    try:
        steam_64_id = int(details['player']['steamid'])
        steam_32_id = steam_64_id % settings.ADDER_32_BIT
        p = Player.objects.get_or_create(steam_id=steam_32_id)
        u = User.objects.get(id=kwargs['user'].id)
        UserProfile.objects.get_or_create(user=u, player=p[0])
        return {'player_created':p[1]}
    except Exception, err:
        print err
