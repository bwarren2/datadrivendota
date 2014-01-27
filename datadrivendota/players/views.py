import json
from functools import wraps
from django.conf import settings
from django.http import  HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import permission_required
from django.db.models import Count
from os.path import basename
from .models import Player, UserProfile
from .r import KDADensity, CountWinrate, PlayerTimeline
from .forms import PlayerWinrateLevers, PlayerTimelineForm, PlayerAddFollowForm
from .json_data import player_winrate_breakout
from matches.models import PlayerMatchSummary, Match
from matches.management.tasks.valve_api_calls import ApiContext, ValveApiCall
from .models import request_to_player
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

@permission_required('players.can_look')
def index(request):
    player_list = Player.objects.filter(updated=True)
    return render(request, 'player_index.html', {'player_list':player_list})

@permission_required('players.can_look')
def detail(request, player_id=None):
    player = get_object_or_404(Player, steam_id=player_id)
    stats = {}
    try:
      wins = PlayerMatchSummary.objects.filter(player=player, match__validity=Match.LEGIT,is_win=True).values('is_win').annotate(Count('is_win'))[0]['is_win__count']
    except IndexError:
      wins = 0
    try:
      losses = PlayerMatchSummary.objects.filter(player=player, match__validity=Match.LEGIT,is_win=False).values('is_win').annotate(Count('is_win'))[0]['is_win__count']
    except IndexError:
      losses = 0

    stats['wins'] = wins
    stats['losses'] = losses
    stats['winrate'] = wins/(wins+losses) if wins+losses>0 else 0

    kda = KDADensity(player.steam_id)
    kdabase = basename(kda.name)
    winrate = CountWinrate(player.steam_id)
    winratebase = basename(winrate.name)
    return render(request, 'player_detail.html', {'player':player,
                               'kdabase':kdabase,
                               'kda':kda,
                               'winratebase':winratebase,
                               'winrate':winrate,
                               'stats':stats})

@permission_required('players.can_touch')
@devserver_profile(follow=[CountWinrate])
def winrate(request):
    chart_spec = """
        {title: "",
    dom: "chart",
    width: 800,
    height: 600,
    layers: [{
            data: chartdata,
            type: "point",
            x: "x_var",
            y: "y_var",
            size:{const:4},
        }],

    }
    """

    if request.method == 'POST':
        winrate_form = PlayerWinrateLevers(request.POST)
        if winrate_form.is_valid():
            return_json = player_winrate_breakout(
              player_id = winrate_form.cleaned_data['player'],
              game_mode_list = winrate_form.cleaned_data['game_modes'],
              min_date = winrate_form.cleaned_data['min_date'],
              max_date = winrate_form.cleaned_data['max_date'],
            )
            return render(request, 'player_form.html', {'form': winrate_form,
                                    'json_data': return_json,
                                    'chart_spec': chart_spec,
                                      'title':'Hero Winrate'})

    else:
        winrate_form = PlayerWinrateLevers()

    return render(request, 'player_form.html', {'form': winrate_form,
                                       'title':'Hero Winrate'})

@permission_required('players.can_touch')
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
            return render(request, 'player_form.html', {'form': timeline_form,
                                      'imagebase': imagebase,
                                      'title':'Player Timeline',})
    else:
        timeline_form = PlayerTimelineForm()

    return render(request, 'player_form.html', {'form': timeline_form,
                              'title':'Player Timeline'})

@permission_required('players.can_look')
def player_matches(request,player_id=None):
  player = get_object_or_404(Player, steam_id=player_id)
  pms_list = PlayerMatchSummary.objects.select_related()
  pms_list = pms_list.filter(player=player).order_by('-match__start_time')[0:50]
  for pms in pms_list:
      pms.display_date = datetime.datetime.fromtimestamp(pms.match.start_time)
      pms.display_duration = str(datetime.timedelta(seconds=pms.match.duration))
      pms.kda2 = pms.kills - pms.deaths+ pms.assists/2.0
      pms.color_class = 'pos' if pms.kda2 > 0 else 'neg'
      pms.mag = abs(pms.kda2)*2
  return render(request, 'playermatchsummary_index.html', {'pms_list':pms_list,
    'player':player})

@permission_required('players.can_look')
def player_management(request):

  player = request_to_player(request)
  if player is not None:
    if request.method == 'POST':
      form = PlayerAddFollowForm(request.POST)
      if form.is_valid():
        follow_player_id = form.cleaned_data['player']
        follow_player= Player.objects.get(steam_id=follow_player_id)
        player.userprofile.following.add(follow_player)
    form = PlayerAddFollowForm()
    follow_list = [follow for follow in player.userprofile.following.all()]
    track_list = [track for track in player.userprofile.tracking.all()]
    return render(request, 'player_management.html', {'follow_list': follow_list,
      'track_list': track_list,
      'track_limit': player.userprofile.track_limit,
      'form': form})
  else:
    return render(request, 'player_management.html', {'error':'You need to be logged in to edit stuff here.'})

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


def drop_follow(request):
    if request.is_ajax():
        drop = Player.objects.get(steam_id=request.POST['slug'])
        request.user.userprofile.following.remove(drop)
        data=request.POST['slug']
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def check_id(request):
    if request.is_ajax() and request.POST['steam_id']!='':
      steam_id = request.POST['steam_id']
      c = ApiContext()
      c.steamids="{base},{check}".format(base=steam_id,check=int(steam_id)+settings.ADDER_32_BIT)
      vac = ValveApiCall()
      t = vac.delay(api_context=c,mode='GetPlayerSummaries')
      steam_response=t.get()

      if steam_response['response']['players'] == []:
        params = {
          'player_exists': False,
          'steam_id': None,
          'name': None,
          'avatar_url': None,
          'public': False,
          'tracked': False
        }
        data = json.dumps(params)
      else:
        c = ApiContext()
        c.account_id=steam_id
        c.matches_requested=1
        c.matches_desired=1
        vac = ValveApiCall()
        t = vac.delay(api_context=c,mode='GetMatchHistory')
        dota_response = t.get()

        tracking = len(UserProfile.objects.filter(tracking__steam_id=steam_id)) != 0 or \
        len(Player.objects.filter(steam_id=steam_id,updated=True))!=0
        if dota_response['result']['status'] != 1:
          params = {
            'player_exists': True,
            'steam_id': steam_response['response']['players'][0]['steamid'],
            'name': steam_response['response']['players'][0]['personaname'],
            'avatar_url': steam_response['response']['players'][0]['avatarmedium'],
            'public': False,
            'tracked': tracking
          }
          data = json.dumps(params)
        else:
          params = {
            'player_exists': True,
            'steam_id': steam_response['response']['players'][0]['steamid'],
            'name': steam_response['response']['players'][0]['personaname'],
            'avatar_url': steam_response['response']['players'][0]['avatarmedium'],
            'public': True,
            'tracked': tracking
          }
          data = json.dumps(params)
      if params['player_exists'] and params['public'] and not params['tracked']:
        data = """<tr>
          <td>{exists}</td>
          <td>{id}</td>
          <td>{name}</td>
          <td><img src='{image}'></td>
          <td>{public}</td>
          <td>{tracked}</td>
          <td><input type="button" id="add_track" name="{id}" value="Import!" /></td>
          </tr>""".format(exists=params['player_exists'],
            id=params['steam_id'],
            name=params['name'],
            public=params['public'],
            image=params['avatar_url'],
            tracked=params['tracked'],
            )
      else:
        data = """<tr>
          <td>{exists}</td>
          <td>{id}</td>
          <td>{name}</td>
          <td><img src='{image}'></td>
          <td>{public}</td>
          <td>{tracked}</td>
          <td>Not available</td>
          </tr>""".format(exists=params['player_exists'],
            id=params['steam_id'],
            name=params['name'],
            public=params['public'],
            image=params['avatar_url'],
            tracked=params['tracked'],
            )

    else:
        data = 'fail'
        mimetype = 'application/json'
        return HttpResponseNotFound(data, mimetype)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def add_track(request):
    if request.is_ajax():
        steam_id = int(request.POST['steam_id']) % settings.ADDER_32_BIT
        try:
          track = Player.objects.get(steam_id=steam_id)
        except Player.DoesNotExist:
          track = Player.objects.create(steam_id=steam_id)
        request.user.userprofile.tracking.add(track)
        data=request.POST['steam_id']
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
