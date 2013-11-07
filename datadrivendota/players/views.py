import json
from functools import wraps
from django.conf import settings
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render
from os.path import basename
from .models import Player
from .r import KDADensity, CountWinrate, PlayerTimeline
from urllib import unquote
from .forms import PlayerWinrateLevers, PlayerTimelineForm
from matches.models import PlayerMatchSummary
import datetime
try:
    if 'devserver' not in settings.INSTALLED_APPS:
        raise ImportError
    from devserver.modules.profile import devserver_profile
except ImportError:
    class devserver_profile(object):
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return wraps(func)(nothing)


def index(request):
    player_list = Player.objects.filter(updated=True)
    return render('player_index.html', {'player_list':player_list})

def detail(request, player_name=None, player_id=None):
    player = validate_player_credentials(player_name, player_id)
    kda = KDADensity(player.steam_id)
    kdabase = basename(kda.name)
    winrate = CountWinrate(player.steam_id)
    winratebase = basename(winrate.name)
    return render('player_detail.html', {'player':player,
                               'kdabase':kdabase,
                               'kda':kda,
                               'winratebase':winratebase,
                               'winrate':winrate})


@devserver_profile(follow=[CountWinrate])
def winrate(request):
    if request.method == 'POST':
        winrate_form = PlayerWinrateLevers(request.POST)
        if winrate_form.is_valid():
            image = CountWinrate(
              player_id = winrate_form.cleaned_data['player'],
              game_mode_list = winrate_form.cleaned_data['game_modes'],
              min_date = winrate_form.cleaned_data['min_date'],
              max_date = winrate_form.cleaned_data['max_date'],
            )
            imagebase = basename(image.name)
            return render('player_form.html', {'form': winrate_form,
                                      'imagebase': imagebase,
                                      'title':'Hero Winrate'})

    else:
        winrate_form = PlayerWinrateLevers()

    return render('player_form.html', {'form': winrate_form,
                                       'title':'Hero Winrate'})

@devserver_profile(follow=[PlayerTimeline])
def timeline(request):
    if request.method == 'POST':
        timeline_form = PlayerTimelineForm(request.POST)
        if timeline_form.is_valid():
            image = PlayerTimeline(
              player_id=timeline_form.cleaned_data['player'],
              min_date=timeline_form.cleaned_data['min_date'],
              max_date=timeline_form.cleaned_data['max_date'],
              bucket_var=timeline_form.cleaned_data['bucket_var'],
              plot_var=timeline_form.cleaned_data['plot_var']
            )
            imagebase = basename(image.name)
            return render('player_form.html', {'form': timeline_form,
                                      'imagebase': imagebase,
                                      'title':'Player Timeline',})
    else:
        timeline_form = PlayerTimelineForm()

    return render('player_form.html', {'form': timeline_form,
                              'title':'Player Timeline'})

def player_matches(request, player_name=None, player_id=None):
  player = validate_player_credentials(player_name, player_id)
  pms_list = PlayerMatchSummary.objects.select_related()
  pms_list = pms_list.filter(player=player).order_by('-match__start_time')[0:50]
  for pms in pms_list:
      print pms.match.steam_id, pms.hero
      pms.display_date = datetime.datetime.fromtimestamp(pms.match.start_time)
      pms.display_duration = str(datetime.timedelta(seconds=pms.match.duration))
      pms.kda2 = pms.kills - pms.deaths+ pms.assists/2.0
      pms.color_class = 'pos' if pms.kda2 > 0 else 'neg'
      pms.mag = abs(pms.kda2)*2
  return render(request, 'playermatchsummary_index.html', {'pms_list':pms_list,
    'persona_name':player.persona_name})

def player_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        players = Player.objects.filter(persona_name__icontains = q )[:20]
        results = []
        for player in players:
            player_json = {}
            player_json['id'] = player.steam_id
            player_json['label'] = player.persona_name
            player_json['value'] = player.persona_name
            results.append(player_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def validate_player_credentials(player_name, player_id):
    if player_name == None and player_id == None:
        return HttpResponseNotFound('<h1>I need either a player name or player id.</h1>')
    elif player_id != None:
        player = get_object_or_404(Player, steam_id=player_id)
    else:
        player_name = unquote(player_name).decode('utf-8')
        player = get_object_or_404(Player, persona_name=player_name)
    return player
