#from django.views.generic.detail import DetailView
from os.path import basename
from django.shortcuts import get_object_or_404, render_to_response
from .models import Hero
from django.utils.text import slugify
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from .forms import HeroVitalsMultiSelect, HeroLineupMultiSelect
from .r import generateChart, lineupChart


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


def vitals(request):

    if request.method == 'POST':
        hero_form = HeroVitalsMultiSelect(request.POST)
        if HeroVitalsMultiSelect(request.POST).is_valid():
          hero_list = hero_form.data.getlist('heroes')
          stat_list = hero_form.data.getlist('stats')
          image = generateChart(hero_list, stat_list)
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

def lineup(request):

    if request.method == 'POST':
        hero_form = HeroLineupMultiSelect(request.POST)
        if HeroLineupMultiSelect(request.POST).is_valid():
          hero_list = hero_form.data.getlist('heroes')
          stat_list = hero_form.data.getlist('stats')
          level =  hero_form.data.getlist('level')
          image = lineupChart(hero_list, stat_list, level)
          imagebase = basename(image.name)
          pass
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
