#from django.views.generic.detail import DetailView
from os.path import basename
import json
from functools import wraps


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.contrib.auth.decorators import login_required
from .models import Hero
from matches.models import GameMode

from .forms import HeroVitalsMultiSelect, HeroLineupMultiSelect, \
  HeroPlayerPerformance, HeroPlayerSkillBarsForm
from .r import generateChart, lineupChart, HeroPerformanceChart,\
 HeroSkillLevelBwChart, speedtest1Chart, speedtest2Chart

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
    hero_list = Hero.objects.all().order_by('name')

    return render(request, 'hero_index.html', {'hero_list': hero_list})


@login_required
def detail(request, hero_name):
    hero_slug = slugify(hero_name)
    current_hero = get_object_or_404(Hero, machine_name=hero_slug)
    game_modes = GameMode.objects.filter(is_competitive=True)
    game_mode_list = [gm.steam_id for gm in game_modes]
    image = HeroPerformanceChart(
              hero = current_hero.steam_id,
              player=None,
              game_mode_list = game_mode_list,
              x_var= 'duration',
              y_var = 'kills',
              group_var = 'skill',
              split_var = 'is_win',
            )
    killsbase = basename(image.name)
    image = HeroPerformanceChart(
              hero = current_hero.steam_id,
              player=None,
              game_mode_list = game_mode_list,
              x_var= 'hero_dmg',
              y_var = 'kills',
              group_var = 'skill',
              split_var = 'is_win',
            )
    dmgbase = basename(image.name)
    return render(request, 'heroes_detail.html', {'hero': current_hero,
                           'killsbase': killsbase,
                           'dmgbase': dmgbase})

@devserver_profile(follow=[generateChart])
def vitals(request):

    if request.method == 'POST':
        hero_form = HeroVitalsMultiSelect(request.POST)
        if hero_form.is_valid():

          linked_scales = hero_form.data.getlist('unlinked_scales')
          display_options = {}
          if linked_scales==[u'on']:
              display_options['linked_scales']="relation='free'"
          else:
              display_options['linked_scales']=''

          image = generateChart(
              hero_list = hero_form.cleaned_data['heroes'],
              stats_list = hero_form.cleaned_data['stats'],
              display_options=display_options
          )
          imagebase = basename(image.name)
          return render(request, 'hero_form.html', {'form': hero_form,
                                    'hero_list': hero_list,
                                    'imagebase': imagebase,
                                    'title':"Hero Vitals"})
    else:
        hero_form = HeroVitalsMultiSelect()
    return render(request, 'hero_form.html', {'form': hero_form,
                                                'title':"Hero Vitals"})

@devserver_profile(follow=[lineupChart])
def lineup(request):

    if request.method == 'POST':
        hero_form = HeroLineupMultiSelect(request.POST)
        if hero_form.is_valid():
          image = lineupChart(
            heroes = hero_form.cleaned_data['heroes'],
            stat = hero_form.cleaned_data['stats'],
            level =  hero_form.cleaned_data['level']
          )

          imagebase = basename(image.name)
          return render(request, 'hero_form.html', {'form': hero_form,
                                    'imagebase': imagebase,
                                    'title':'Hero Lineups'})
    else:
        hero_form = HeroLineupMultiSelect()

    return render(request, 'hero_form.html', {'form': hero_form,
                                                 'title':'Hero Lineups'})

@devserver_profile(follow=[HeroPerformanceChart])
def hero_performance(request):
    if request.method=='POST':
        hero_form = HeroPlayerPerformance(request.POST)
        if hero_form.is_valid():
            image = HeroPerformanceChart(
              hero = hero_form.cleaned_data['hero'],
              player = hero_form.cleaned_data['player'],
              game_mode_list = hero_form.cleaned_data['game_modes'],
              x_var= hero_form.cleaned_data['x_var'],
              y_var = hero_form.cleaned_data['y_var'],
              group_var = hero_form.cleaned_data['group_var'],
              split_var = hero_form.cleaned_data['split_var'],
            )
            imagebase = basename(image.name)
            return render(request, 'hero_form.html',{'form': hero_form,
                                      'imagebase': imagebase,
                                      'title':'Hero Performance'})
    else:
      hero_form = HeroPlayerPerformance()

    return render(request, 'hero_form.html',{'form': hero_form,
                                                'title':'Hero Performance'})

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

@devserver_profile(follow=[speedtest1Chart])
def speedtest1(request):
    image = speedtest1Chart()
    imagebase = basename(image.name)
    return render(request, 'speedtest.html',
                              {'imagebase': imagebase})

@devserver_profile(follow=[speedtest2Chart, render])
def speedtest2(request):
    image = speedtest2Chart()
    imagebase = basename(image.name)
    return render(request, 'speedtest.html',
                              {'imagebase': imagebase})


def hero_list(request):

    if request.is_ajax():
        q = request.GET.get('term', '')
        heroes = Hero.objects.filter(name__icontains = q )[:20]
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
