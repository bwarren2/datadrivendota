#from django.views.generic.detail import DetailView
from os.path import basename
import json
from functools import wraps


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.contrib.auth.decorators import permission_required
from datadrivendota.utilities import NoDataFound
from .models import Hero, Ability
from matches.models import GameMode
from .json_data import hero_vitals_json, hero_lineup_json, hero_performance_json

from .forms import HeroVitalsMultiSelect, HeroLineupMultiSelect, \
  HeroPlayerPerformance, HeroPlayerSkillBarsForm
from .r import  HeroPerformanceChart,\
 HeroSkillLevelBwChart
try:
    if 'devserver' not in settings.INSTALLED_APPS or not settings.DEBUG:
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
    hero_list = Hero.objects.all().order_by('name')

    return render(request, 'hero_index.html', {'hero_list': hero_list})


@permission_required('players.can_look')
#@devserver_profile(follow=[HeroPerformanceChart])
def detail(request, hero_name):
    hero_slug = slugify(hero_name)
    current_hero = get_object_or_404(Hero, machine_name=hero_slug)
    abilities = Ability.objects.filter(is_core=True,hero=current_hero)
    charts = []
    return render(request, 'heroes_detail.html', {'hero': current_hero,
                           'abilities': abilities,
                           'charts':charts})

@permission_required('players.can_look')
#@devserver_profile(follow=[generateChart])
def vitals(request):

    chart_spec = """
    {title: "",
dom: "chart",
width: 800,
height: 600,
layers: [{
        data: chartdata,
        type: "point",
        x: "level",
        y: "value",
        color: "hero",
        size:{const:5},
        sample:1000,
    },
    {
        data: chartdata,
        type: "line",
        x: "level",
        y: "value",
        color: "hero",
        size:{const:3},
    }],

    facet:{
      type:'wrap',
      var:'stat',
      formatter: function(facetObject) {
            var title = facetObject.stat;
            return title;
        }
    }
}
"""


    if request.method == 'POST':
        hero_form = HeroVitalsMultiSelect(request.POST)
        if hero_form.is_valid():
          try:
            return_json = hero_vitals_json(
                hero_list = hero_form.cleaned_data['heroes'],
                stats_list = hero_form.cleaned_data['stats'],
            )
            return render(request, 'hero_form.html', {'form': hero_form,
                                      'json_data': return_json,
                                      'chart_spec': chart_spec,
                                      'title':"Hero Vitals"})
          except NoDataFound:
            return render(request, 'hero_form.html', {'form': hero_form,
                          'json_data': return_json,
                          'chart_spec': chart_spec,
                          'title':"Hero Vitals"})

    else:
        hero_form = HeroVitalsMultiSelect()
    return render(request, 'hero_form.html', {'form': hero_form,
                                                'title':"Hero Vitals"})

@permission_required('players.can_look')
#@devserver_profile(follow=[lineupChart])
def lineup(request):

    chart_spec = """
    {title: "",
dom: "chart",
width: 800,
height: 600,
layers: [
    {
        data: chartdata,
        type: "bar",
        x: {'var':'HeroName', sort:'Value', asc: false},
        y: "Value",
        color: "Color",
        sample:1000,
    }],

}
"""

    if request.method == 'POST':
        hero_form = HeroLineupMultiSelect(request.POST)
        if hero_form.is_valid():
          return_json = hero_lineup_json(
            heroes = hero_form.cleaned_data['heroes'],
            stat = hero_form.cleaned_data['stats'],
            level =  hero_form.cleaned_data['level']
          )

          return render(request, 'hero_form.html', {'form': hero_form,
                                    'json_data': return_json,
                                    'chart_spec': chart_spec,
                                    'title':'Hero Lineups'})
    else:
        hero_form = HeroLineupMultiSelect()

    return render(request, 'hero_form.html', {'form': hero_form,
                                                 'title':'Hero Lineups'})

@permission_required('players.can_touch')
@devserver_profile(follow=[hero_performance_json])
def hero_performance(request):

    if request.method=='POST':
        hero_form = HeroPlayerPerformance(request.POST)
        if hero_form.is_valid():
            return_json, x, y, group, split = hero_performance_json(
              hero = hero_form.cleaned_data['hero'],
              player = hero_form.cleaned_data['player'],
              game_mode_list = hero_form.cleaned_data['game_modes'],
              x_var= hero_form.cleaned_data['x_var'],
              y_var = hero_form.cleaned_data['y_var'],
              group_var = hero_form.cleaned_data['group_var'],
              split_var = hero_form.cleaned_data['split_var'],
            )

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
                    size:{const:4},
                    sample:1000,
                }],

                facet:{
                  type:'wrap',
                  var:'split_var',
                  formatter: function(facetObject) {
                        var title = facetObject.split_var;
                        return title;
                    }
                },
                guides:{
                  x:{'title':'"""+x+"""'},
                  y:{'title':'"""+y+"""'}
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
            return render(request, 'hero_form.html',{'form': hero_form,
                                    'json_data': return_json,
                                    'chart_spec': chart_spec,
                                    'extra_chart_js': extra_chart_js,
                                    'title':'Hero Performance'})
    else:
      hero_form = HeroPlayerPerformance()

    return render(request, 'hero_form.html',{'form': hero_form,
                                                'title':'Hero Performance'})

@permission_required('players.can_touch')
@devserver_profile(follow=[HeroSkillLevelBwChart])
def hero_skill_bars(request):
    if request.method=='POST':
        hero_form = HeroPlayerSkillBarsForm(request.POST)
        if hero_form.is_valid():
            image = HeroSkillLevelBwChart(
              hero = hero_form.cleaned_data['hero'],
              player = hero_form.cleaned_data['player'],
              game_mode_list = hero_form.cleaned_data['game_modes'],
              levels= hero_form.cleaned_data['levels'],
            )
            imagebase = basename(image.name)
            return render(request, 'hero_form.html',{'form': hero_form,
                                      'imagebase': imagebase,
                                      'title': 'Hero Skill Times'})
    else:
      hero_form = HeroPlayerSkillBarsForm
    return render(request, 'hero_form.html',{'form': hero_form,
                                                'title': 'Hero Skill Times'})


def hero_list(request):

    if request.is_ajax():
        q = request.GET.get('term', '')
        heroes = Hero.objects.filter(name__icontains = q, visible=True)[:20]
        results = []
        for hero in heroes:
            hero_json = {}
            hero_json['id'] = hero.steam_id
            hero_json['label'] = hero.name
            hero_json['value'] = hero.name
            results.append(hero_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)

def hero_performance_api(request):
    if request.is_ajax():
        hero_name = request.GET.get('hero', None)
        x_var = request.GET.get('x_var', None)
        y_var = request.GET.get('y_var', None)
        group_var = request.GET.get('group_var', None)
        split_var = request.GET.get('split_var', None)
        hero = Hero.objects.get(name = hero_name)
        game_modes = GameMode.objects.filter(is_competitive=True)
        game_mode_list = [gm.steam_id for gm in game_modes]
        image = HeroPerformanceChart(
                  hero = hero.steam_id,
                  player=None,
                  game_mode_list = game_mode_list,
                  x_var = x_var,
                  y_var = y_var,
                  group_var = group_var,
                  split_var = split_var,
                  width=350,
                  height=350
                )
        imagebase = basename(image.name)
        response_data = {}
        response_data['result'] = 'success'
        response_data['url'] = settings.MEDIA_URL+imagebase
        return HttpResponse(json.dumps(response_data), content_type="application/json")
    else:
        data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

def ability_detail(request, ability_name):
    ability = get_object_or_404(Ability, machine_name=ability_name)
    charts = []
    return render(request, 'ability_detail.html', {'ability': ability,
                           'charts':charts})
