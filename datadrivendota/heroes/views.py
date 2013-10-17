#from django.views.generic.detail import DetailView
from os.path import basename
import json
from functools import wraps


from django.conf import settings
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
        if hero_form.is_valid():

          linked_scales = hero_form.data.getlist('unlinked_scales')
          display_options = {}
          if linked_scales==[u'on']:
              display_options['linked_scales']="relation='free'"
          else:
              display_options['linked_scales']=''

          image = generateChart(
             hero_list = hero_form.cleaned_data['heroes'],
              stat_list = hero_form.cleaned_data['stats'],
              display_options=display_options
          )
          imagebase = basename(image.name)
          return render_to_response('hero_vitals.html', {'form': hero_form,
                                    'hero_list': hero_list, 'image': image,
                                    'imagebase': imagebase},
                                    context_instance=RequestContext(request))
    else:
        hero_form = HeroVitalsMultiSelect()
    return render_to_response('hero_vitals.html', {'form': hero_form},
                               context_instance=RequestContext(request))

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
          return render_to_response('hero_lineups.html', {'form': hero_form,
                                    'image': image,
                                    'imagebase': imagebase},
                                    context_instance=RequestContext(request))
    else:
        hero_form = HeroLineupMultiSelect()

    return render_to_response('hero_lineups.html', {'form': hero_form},
                              context_instance=RequestContext(request))

@devserver_profile(follow=[HeroPerformanceChart])
def hero_performance(request):
    if request.method=='POST':
        hero_form = HeroPlayerPerformance(request.POST)
        if hero_form.is_valid():
            image = HeroPerformanceChart(
              player_name = hero_form.cleaned_data['player'],
              game_mode_list = hero_form.cleaned_data['game_modes'],
              x_var= hero_form.cleaned_data['x_var'],
              y_var = hero_form.cleaned_data['y_var'],
              group_var = hero_form.cleaned_data['group_var'],
              split_var = hero_form.cleaned_data['split_var'],
            )
            imagebase = basename(image.name)
            return render_to_response('hero_performance.html',{'form': hero_form,
                                      'image': image,
                                      'imagebase': imagebase},
                                      context_instance=RequestContext(request))
    else:
      hero_form = HeroPlayerPerformance()

    return render_to_response('hero_performance.html',{'form': hero_form},
                              context_instance=RequestContext(request))

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
            return render_to_response('hero_skill_time_bars.html',{'form': hero_form,
                                      'image': image,
                                      'imagebase': imagebase},
                                      context_instance=RequestContext(request))
    else:
      hero_form = HeroPlayerSkillBarsForm
    return render_to_response('hero_skill_time_bars.html',{'form': hero_form},
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
