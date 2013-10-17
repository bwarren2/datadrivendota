import datetime
from os.path import basename
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from .forms import EndgameSelect
from .r import EndgameChart
from .models import Match, PlayerMatchSummary
# Create your views here.

def match(request, match_id):
    match = get_object_or_404(Match, steam_id=match_id)
    summaries = get_list_or_404(PlayerMatchSummary, match=match)
    for summary in summaries:
        summary.kda = summary.kills - summary.deaths + .5*summary.assists
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(match.start_time).strftime('%H:%M:%S %Y-%m-%d')
    return render_to_response('match_detail.html', {'match':match,
                              'summaries':summaries
                              },
                              context_instance=RequestContext(request))

def index(request):
    match_list = Match.objects.all()[:10]
    return render_to_response('matches_index.html', {'match_list': match_list},
                              context_instance=RequestContext(request))

def endgame(request):
    if request.method == 'POST':
        select_form = EndgameSelect(request.POST)
        if select_form.is_valid():

            image = EndgameChart(
                player_list = select_form.cleaned_data['players'],
                mode_list = select_form.cleaned_data['game_modes'],
                x_var = select_form.cleaned_data['x_var'],
                y_var = select_form.cleaned_data['y_var'],
                split_var = select_form.cleaned_data['split_var'],
                group_var = select_form.cleaned_data['group_var'],
            )
            imagebase = basename(image.name)
            return render_to_response('endgames.html',
                                     {'form':select_form,'image':image,
                                      'imagebase':imagebase
                                     },
                                    context_instance=RequestContext(request))

    else:
        select_form = EndgameSelect()
    return render_to_response('endgames.html',
                             {'form':select_form},
                            context_instance=RequestContext(request))

