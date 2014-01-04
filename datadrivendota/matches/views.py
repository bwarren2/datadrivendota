import datetime
from functools import wraps
from os.path import basename
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, get_list_or_404, render
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from .forms import EndgameSelect, TeamEndgameSelect
from .r import EndgameChart, MatchParameterScatterplot, TeamEndgameChart
from .models import Match, PlayerMatchSummary
from .json_data import player_endgame_json, team_endgame_json
from players.models import request_to_player
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
def match(request, match_id):
    match = get_object_or_404(Match, steam_id=match_id)
    summaries = get_list_or_404(PlayerMatchSummary, match=match)
    for summary in summaries:
        summary.kda = summary.kills - summary.deaths + .5*summary.assists
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(match.start_time).strftime('%H:%M:%S %Y-%m-%d')
    kill_dmg_chart = MatchParameterScatterplot(match_id, 'kills', 'hero_damage')
    kdc_basename = basename(kill_dmg_chart.name)
    xp_gold_chart = MatchParameterScatterplot(match_id, 'gold_per_min', 'xp_per_min')
    xg_basename = basename(xp_gold_chart.name)
    return render(request, 'match_detail.html', {'match':match,
                              'summaries':summaries,
                              'kill_dmg_chart': kill_dmg_chart,
                              'kdc_basename': kdc_basename,
                              'xp_gold_chart': xp_gold_chart,
                              'xg_basename': xg_basename,
                              })

@permission_required('players.can_look')
def index(request):

    player = request_to_player(request)
    if player is not None:
      follow_list = [follow for follow in player.following.all()]
      match_list = Match.objects.filter(validity=Match.LEGIT, playermatchsummary__player__in=follow_list)
      match_list = match_list.select_related().distinct()[:100]


      paginator = Paginator(match_list, 10)
      page = request.GET.get('page')
      try:
          match_list = paginator.page(page)
      except PageNotAnInteger:
          # If page is not an integer, deliver first page.
          match_list = paginator.page(1)
      except EmptyPage:
          # If page is out of range (e.g. 9999), deliver last page of results.
          match_list = paginator.page(paginator.num_pages)

      for match in match_list:
        match.follow_annotations=[]
        match.display_date = datetime.datetime.fromtimestamp(match.start_time)
        match.display_duration = str(datetime.timedelta(seconds=match.duration))
        for pms in match.playermatchsummary_set.all():
          if pms.player in follow_list:
            follow_data = {'player_image':pms.player.avatar,
                           'hero_image':pms.hero.thumbshot.url,
                           'KDA':pms.kills-pms.deaths+pms.assists/2.0}
            match.follow_annotations.append(follow_data)

      return render(request, 'matches_index.html', {'match_list': match_list})

    else:
      match_list = Match.objects.filter(validity=Match.LEGIT)[:100]

      paginator = Paginator(match_list, 10)
      page = request.GET.get('page')
      try:
          match_list = paginator.page(page)
      except PageNotAnInteger:
          # If page is not an integer, deliver first page.
          match_list = paginator.page(1)
      except EmptyPage:
          # If page is out of range (e.g. 9999), deliver last page of results.
          match_list = paginator.page(paginator.num_pages)


      for match in match_list:
        match.display_date = datetime.datetime.fromtimestamp(match.start_time)
        match.display_duration = str(datetime.timedelta(seconds=match.duration))
      return render(request, 'matches_index.html', {'match_list': match_list})

@permission_required('players.can_touch')
@devserver_profile(follow=[EndgameChart])
def endgame(request):

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
        color: "group_var",
        size:{const:3},
        opacity:{const:3},
    }],

    facet:{
      type:'wrap',
      var:'split_var',
      formatter: function(facetObject) {
            var title = facetObject.split_var;
            return title;
        }
    }
}
    """
    extra_chart_js= """tester = function(type, obj, event, chart){
  data = obj.evtData;
  if (type ==="click"){
    top.location="/matches/"+String(data.match_id["in"]);
  }
}
chart.addHandler(tester)"""


    if request.method == 'POST':
        select_form = EndgameSelect(request.POST)
        if select_form.is_valid():

            return_json = player_endgame_json(
                player_list = select_form.cleaned_data['players'],
                mode_list = select_form.cleaned_data['game_modes'],
                x_var = select_form.cleaned_data['x_var'],
                y_var = select_form.cleaned_data['y_var'],
                split_var = select_form.cleaned_data['split_var'],
                group_var = select_form.cleaned_data['group_var'],
            )[0]
            return render(request, 'match_form.html',
                                     {'form':select_form,
                                    'json_data': return_json,
                                    'chart_spec': chart_spec,
                                    'extra_chart_js': extra_chart_js,
                                    'title':'Endgame Charts'
                                     })

    else:
        select_form = EndgameSelect()
    return render(request, 'match_form.html',
      {'form':select_form,'title':'Endgame Charts'})

@permission_required('players.can_touch')
@devserver_profile(follow=[team_endgame_json])
def team_endgame(request):

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
        color: "group_var",
        size:{const:3},
        opacity:{const:3},
    }],

    facet:{
      type:'wrap',
      var:'split_var',
      formatter: function(facetObject) {
            var title = facetObject.split_var;
            return title;
        }
    }
}
    """
    extra_chart_js= """tester = function(type, obj, event, chart){
  data = obj.evtData;
  if (type ==="click"){
    window.open("/matches/"+String(data.match_id["in"]));
  }
}
chart.addHandler(tester)"""

    if request.method == 'POST':
        select_form = TeamEndgameSelect(request.POST)
        if select_form.is_valid():

            return_json, xlab, ylab, grouplab = team_endgame_json(
                player_list = select_form.cleaned_data['players'],
                mode_list = select_form.cleaned_data['game_modes'],
                x_var = select_form.cleaned_data['x_var'],
                y_var = select_form.cleaned_data['y_var'],
                split_var = select_form.cleaned_data['split_var'],
                group_var = select_form.cleaned_data['group_var'],
                compressor = select_form.cleaned_data['compressor'],
            )

            return render(request, 'match_form.html',
                                     {'form':select_form,
                                    'json_data': return_json,
                                    'chart_spec': chart_spec,
                                    'extra_chart_js': extra_chart_js,
                                      'title':'Endgame Charts'
                                     })

    else:
        select_form = TeamEndgameSelect()
    return render(request, 'match_form.html',
      {'form':select_form,'title':'Endgame Charts'})

