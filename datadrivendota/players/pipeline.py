from players.models import Player
from django.conf import settings

def create_player(strategy, details, response, *args, **kwargs):
    steam_64_id = int(details['player']['steamid'])
    steam_32_id = steam_64_id % settings.ADDER_32_BIT
    p = Player.objects.get_or_create(steam_id=steam_32_id)
    return {'player_created':p[1]}
