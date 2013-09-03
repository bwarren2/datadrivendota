# Create your views here.
from django.http import HttpResponseNotFound
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from os.path import basename
from .models import Player
from .r import KDADensity, CountWinrate

def index(request):
    return render_to_response('player_index.html', {'words':"Nope."},
                              context_instance = RequestContext(request))

def detail(request, player_name=None, player_id=None):
    if player_name == None and player_id == None:
        return HttpResponseNotFound('<h1>I need either a player name or player id.</h1>')
    elif player_id != None:
        player = get_object_or_404(Player, steam_id=player_id)
    else:
        player = get_object_or_404(Player, persona_name=player_name)

    kda = KDADensity(player.steam_id)
    kdabase = basename(kda.name)
    winrate = CountWinrate(player.steam_id)
    winratebase = basename(winrate.name)
    return render_to_response('player_detail.html', {'player':player,
                               'kdabase':kdabase,
                               'kda':kda,
                               'winratebase':winratebase,
                               'winrate':winrate},
                              context_instance = RequestContext(request))

