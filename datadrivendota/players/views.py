# Create your views here.
import json
from django.http import HttpResponseNotFound, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from os.path import basename
from .models import Player
from .r import KDADensity, CountWinrate, PlayerTimeline
from urllib import unquote
from .forms import PlayerWinrateLevers, PlayerTimelineForm
def index(request):
    player_list = Player.objects.filter(updated=True)
    return render_to_response('player_index.html', {'player_list':player_list},
                              context_instance = RequestContext(request))

def detail(request, player_name=None, player_id=None):
    if player_name == None and player_id == None:
        return HttpResponseNotFound('<h1>I need either a player name or player id.</h1>')
    elif player_id != None:
        player = get_object_or_404(Player, steam_id=player_id)
    else:
        player_name = unquote(player_name).decode('utf-8')[:-1]
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

def winrate(request):

    if request.method == 'POST':
        winrate_form = PlayerWinrateLevers(request.POST)
        if winrate_form.is_valid():
            player_name = winrate_form.cleaned_data['player']
            min_date = winrate_form.cleaned_data['min_date']
            max_date = winrate_form.cleaned_data['max_date']
            game_modes = winrate_form.cleaned_data['game_modes']
            player = Player.objects.filter(persona_name=player_name)
            image = CountWinrate(player[0].steam_id, min_date, max_date, game_modes)
            imagebase = basename(image.name)

        else:
          image = ''
          imagebase = ''
    else:
        winrate_form = PlayerWinrateLevers()
        image = ''
        imagebase = ''

    return render_to_response('winrate_chart.html', {'form': winrate_form,
                              'image': image,
                              'imagebase': imagebase},
                              context_instance=RequestContext(request))

def timeline(request):

    if request.method == 'POST':
        timeline_form = PlayerTimelineForm(request.POST)
        if timeline_form.is_valid():
            player_name=timeline_form.cleaned_data['player']
            player_id=get_object_or_404(Player,persona_name=player_name).steam_id
            min_date=timeline_form.cleaned_data['min_date']
            max_date=timeline_form.cleaned_data['max_date']
            bucket_var=timeline_form.cleaned_data['bucket_var']
            plot_var=timeline_form.cleaned_data['plot_var']
            image = PlayerTimeline(player_id, min_date, max_date, bucket_var, plot_var)
            imagebase = basename(image.name)

        else:
          image = ''
          imagebase = ''
    else:
        timeline_form = PlayerTimelineForm()
        image = ''
        imagebase = ''

    return render_to_response('player_timeline_chart.html', {'form': timeline_form,
                              'image': image,
                              'imagebase': imagebase,
                              'title':'Player Timeline',
                              'page_title':'Player Timeline'},
                              context_instance=RequestContext(request))


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
