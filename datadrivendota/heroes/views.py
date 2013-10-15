#from django.views.generic.detail import DetailView
from os.path import basename
import json
from functools import wraps


from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from .models import Hero
from django.utils.text import slugify
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .forms import HeroVitalsMultiSelect, HeroLineupMultiSelect, \
  HeroPlayerPerformance, HeroPlayerSkillBarsForm
from .r import generateChart, lineupChart, HeroPerformanceChart,\
 HeroSkillLevelBwChart
from players.models import Player
from django.conf import settings

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

    return render_to_response('hero_index.html', {'hero_list': hero_list},
                              context_instance=RequestContext(request))


@login_required
def detail(request, hero_name):
    hero_slug = slugify(hero_name)
    current_hero = get_object_or_404(Hero, machine_name=hero_slug)

    return render_to_response('heroes_detail.html', {'hero': current_hero},
                              context_instance=RequestContext(request))

@devserver_profile(follow=[generateChart])
def vitals(request):

    if request.method == 'POST':
        hero_form = HeroVitalsMultiSelect(request.POST)
        if HeroVitalsMultiSelect(request.POST).is_valid():
          hero_list = hero_form.data.getlist('heroes')[0].split(',')
          stat_list = hero_form.data.getlist('stats')
          linked_scales = hero_form.data.getlist('unlinked_scales')
          display_options = {}
          if linked_scales==[u'on']:
              display_options['linked_scales']="relation='free'"
          else:
              display_options['linked_scales']=''
          image = generateChart(hero_list, stat_list, display_options)
          imagebase = basename(image.name)
        else:
          hero_list = []
          image = ''
          imagebase = ''
    else:
        hero_form = HeroVitalsMultiSelect()
        hero_list = []
        image = ''
        imagebase = ''

    return render_to_response('hero_vitals.html', {'form': hero_form,
                              'hero_list': hero_list, 'image': image,
                              'imagebase': imagebase},
                              context_instance=RequestContext(request))

@devserver_profile(follow=[lineupChart])
def lineup(request):

    if request.method == 'POST':
        hero_form = HeroLineupMultiSelect(request.POST)
        if HeroLineupMultiSelect(request.POST).is_valid():
          hero_list = hero_form.data.getlist('heroes')[0].split(',')
          stat_list = hero_form.data.getlist('stats')
          level =  hero_form.data.getlist('level')
          image = lineupChart(hero_list, stat_list, level)
          imagebase = basename(image.name)
        else:
          hero_list = []
          image = ''
          imagebase = ''
    else:
        hero_form = HeroLineupMultiSelect()
        hero_list = []
        image = ''
        imagebase = ''

    return render_to_response('hero_lineups.html', {'form': hero_form,
                              'hero_list': hero_list, 'image': image,
                              'imagebase': imagebase},
                              context_instance=RequestContext(request))

@devserver_profile(follow=[HeroPerformanceChart])
def hero_performance(request):
    if request.method=='POST':
        hero_form = HeroPlayerPerformance(request.POST)
        if hero_form.is_valid():
            hero = Hero.objects.get(name=hero_form.cleaned_data['hero']).steam_id
            player_name = hero_form.cleaned_data['player']
            if player_name is not None and player_name != '':
              player = Player.objects.get(persona_name=player_name).steam_id
            else:
              player=None
            game_mode_list = hero_form.cleaned_data['game_modes']
            x_var= hero_form.cleaned_data['x_var']
            y_var = hero_form.cleaned_data['y_var']
            split_var = hero_form.cleaned_data['split_var']
            group_var = hero_form.cleaned_data['group_var']
            image = HeroPerformanceChart(hero, player, game_mode_list,
              x_var, y_var, group_var, split_var)
            imagebase = basename(image.name)
        else:
            hero_form = HeroPlayerPerformance
            hero = []
            image = ''
            imagebase=''
    else:
      hero_form = HeroPlayerPerformance
      hero = []
      image = ''
      imagebase=''
    return render_to_response('hero_performance.html',{'form': hero_form,
                              'hero': hero, 'image': image,
                              'imagebase': imagebase},
                              context_instance=RequestContext(request))

@devserver_profile(follow=[HeroSkillLevelBwChart])
def hero_skill_bars(request):
    if request.method=='POST':
        hero_form = HeroPlayerSkillBarsForm(request.POST)
        if hero_form.is_valid():
            hero = Hero.objects.get(name=hero_form.cleaned_data['hero']).steam_id
            player_name = hero_form.cleaned_data['player']
            if player_name is not None and player_name != '':
              player = Player.objects.get(persona_name=player_name).steam_id
            else:
              player=None
            game_mode_list = hero_form.cleaned_data['game_modes']
            levels= hero_form.cleaned_data['levels']
            image = HeroSkillLevelBwChart(hero, player, game_mode_list, levels)
            imagebase = basename(image.name)
        else:
            hero_form = HeroSkillLevelBwChart
            hero = []
            image = ''
            imagebase=''
    else:
      hero_form = HeroPlayerSkillBarsForm
      hero = []
      image = ''
      imagebase=''
    return render_to_response('hero_skill_time_bars.html',{'form': hero_form,
                              'hero': hero, 'image': image,
                              'imagebase': imagebase},
                              context_instance=RequestContext(request))

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
