from os.path import basename
import json
from functools import wraps


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from django.contrib.auth.decorators import permission_required
from matches.models import GameMode
from utils.exceptions import NoDataFound
from .json_data import (
    hero_vitals_json,
    hero_lineup_json,
    hero_performance_json,
    hero_progression_json
)
from .models import Hero, Ability, HeroDossier, Role

from .forms import (
    HeroVitalsMultiSelect,
    HeroLineupMultiSelect,
    HeroPlayerPerformance,
    HeroPlayerSkillBarsForm,
    HeroProgressionForm
)
from .r import (
    HeroPerformanceChart,
    HeroSkillLevelBwChart
)
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


def index(request):
    hero_list = Hero.objects.filter(visible=True).order_by('name')\
        .select_related()
    role_list = Role.objects.all()
    return render(request, 'heroes/index.html', {
        'hero_list': hero_list,
        'role_list': role_list,
        })


# @devserver_profile(follow=[HeroPerformanceChart])
def detail(request, hero_name):
    hero_slug = slugify(hero_name)
    current_hero = get_object_or_404(Hero, machine_name=hero_slug)
    abilities = Ability.objects.filter(
        is_core=True,
        hero=current_hero).order_by('steam_id')
    dossier = HeroDossier.objects.get(hero=current_hero)
    charts = []
    return render(
        request,
        'heroes/detail.html',
        {
            'hero': current_hero,
            'abilities': abilities,
            'dossier': dossier,
            'charts': charts,
        }
    )


# @devserver_profile(follow=[generateChart])
def vitals(request):

    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts stat progression for a few heroes by level."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare Slark, Riki, and Phantom Lancer on strength and agility progression."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify what attributes and heroes you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like all heroes lined up for one stat at one level, try these subtabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: how does your favorite hero compare to your least favorite in their primary stats?"
        }
    ]
    tour = json.dumps(tour)
    if request.GET:
        hero_form = HeroVitalsMultiSelect(request.GET)
        if hero_form.is_valid():
            try:
                json_data = hero_vitals_json(
                    hero_list=hero_form.cleaned_data['heroes'],
                    stats_list=hero_form.cleaned_data['stats']
                )
                return render(
                    request,
                    'heroes/form.html',
                    {
                        'form': hero_form,
                        'json_data': basename(json_data.name),
                        'title': "Hero Vitals",
                        'tour': tour
                    }
                )
            except NoDataFound:
                return render(
                    request,
                    'heroes/form.html',
                    {
                        'form': hero_form,
                        'error': 'error',
                        'title': "Hero Vitals",
                        'tour': tour,
                    }
                )

    else:
        hero_form = HeroVitalsMultiSelect()
    return render(
        request,
        'heroes/form.html',
        {
            'form': hero_form,
            'title': "Hero Vitals",
            'tour': tour,
        }
    )


# @devserver_profile(follow=[lineupChart])
def lineup(request):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts all heroes at one level for one stat, so you have a sense of distribution."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can track Ogre Magi's, Ursa's, and Phoenix's strength at levels 1 and 25 on two pages to see how they move in the distribution."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attribute and heroes you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like all levels of a few heroes for a few vital stats, try these subtabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: how do your favorite strength, intelligence, and agility heroes change in strength at various levels?"
        }
    ]
    tour = json.dumps(tour)
    if request.GET:
        hero_form = HeroLineupMultiSelect(request.GET)
        if hero_form.is_valid():
            try:
                json_data = hero_lineup_json(
                    heroes=hero_form.cleaned_data['heroes'],
                    stat=hero_form.cleaned_data['stats'],
                    level=hero_form.cleaned_data['level']
                )

                return render(
                    request,
                    'heroes/form.html',
                    {
                        'form': hero_form,
                        'json_data': basename(json_data.name),
                        'title': 'Hero Lineups',
                        'tour': tour,
                    }
                )
            except NoDataFound:
                return render(
                    request,
                    'heroes/form.html',
                    {
                        'form': hero_form,
                        'error': 'error',
                        'title': 'Hero Lineups',
                        'tour': tour,
                    }
                )

    else:
        hero_form = HeroLineupMultiSelect()

    return render(
        request,
        'heroes/form.html',
        {
            'form': hero_form,
            'title': 'Hero Lineups',
            'tour': tour,
        }
    )


@devserver_profile(follow=[hero_performance_json])
def hero_performance(request):

    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page lets you break out end-of-game data by skill level, according to Valve's skill estimate."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can scatter end-of-game kills vs game time for Alchemist (and include your data to compare)."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and hero you want to render here, optionally adding a player."
        },
        {
            'orphan': True,
            'title': "Important note!",
            'content': "Valve automagically determines their own skill bracketing, with 1-2-3 being low-medium-high."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For other charts, such as head-to-head comparison between players, try other tabs (like the matches:endgame chart).",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: how does your kills-deaths+assists/2 (kda2) on your favorite carry compare to other skill brackets?"
        }
    ]
    tour = json.dumps(tour)
    if request.GET:
        hero_form = HeroPlayerPerformance(request.GET)
        if hero_form.is_valid():
            image = HeroPerformanceChart(
                hero=hero_form.cleaned_data['hero'],
                player=hero_form.cleaned_data['player'],
                game_mode_list=hero_form.cleaned_data['game_modes'],
                x_var=hero_form.cleaned_data['x_var'],
                y_var=hero_form.cleaned_data['y_var'],
                group_var=hero_form.cleaned_data['group_var'],
                split_var=hero_form.cleaned_data['split_var'],
            )
            imagebase = basename(image.name)
            return render(
                request,
                'heroes/form.html',
                {
                    'form': hero_form,
                    'image_name': imagebase,
                    'title': 'Hero Performance',
                    'tour': tour,
                }
            )
    else:
        hero_form = HeroPlayerPerformance()
    return render(
        request,
        'heroes/form.html',
        {
            'tour': tour,
            'form': hero_form,
            'title': 'Hero Performance',
        }
    )


@devserver_profile(follow=[hero_progression_json])
def hero_skill_progression(request):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page is one of the most complicated; do not be overwhelmed!."
        },
        {
            'orphan': True,
            'title': "Purpose",
            'content': "This page plots data from within games, showing when skill points get placed in games for one hero by skill bracket."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can see how quickly high skill Anti-Mage players farm compared to low skill ones, and include your own data (if you are being imported)."
        },
        {
            'orphan': True,
            'title': "Inferences",
            'content': "By observing trends (when farm starts slowing down for a group, or roughly what level high-skill players can reach at any time) you can find room to improve yourself."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which hero you want, and an optional player to compare here."
        },
        {
            'orphan': True,
            'title': "Important note!",
            'content': "The skill designation is given automagically by Valve; 1-2-3 correspond to low-medium-high."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For more player comparisons, try the matches or player sections!",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: for your favorite hero, how many more levels can high-skill players have over low skill players at the 30 minute mark?"
        }
    ]
    tour = json.dumps(tour)
    if request.GET:
        hero_form = HeroProgressionForm(request.GET)
        if hero_form.is_valid():
            json_data = hero_progression_json(
                hero=hero_form.cleaned_data['hero'],
                player=hero_form.cleaned_data['player'],
                game_mode_list=hero_form.cleaned_data['game_modes'],
                division=hero_form.cleaned_data['division'],
            )
            return render(
                request,
                'heroes/form.html',
                {
                    'form': hero_form,
                    'json_data': basename(json_data.name),
                    'title': 'Hero Skilling',
                    'tour': tour,
                }
            )
    else:
        hero_form = HeroProgressionForm()
    return render(
        request,
        'heroes/form.html',
        {
            'form': hero_form,
            'title': 'Hero Performance',
            'tour': tour,
        }
    )


@devserver_profile(follow=[HeroSkillLevelBwChart])
def hero_skill_bars(request):
    if request.GET:
        hero_form = HeroPlayerSkillBarsForm(request.GET)
        if hero_form.is_valid():
            image = HeroSkillLevelBwChart(
                hero=hero_form.cleaned_data['hero'],
                player=hero_form.cleaned_data['player'],
                game_mode_list=hero_form.cleaned_data['game_modes'],
                levels=hero_form.cleaned_data['levels'],
            )
            imagebase = basename(image.name)
            return render(
                request,
                'heroes/form.html',
                {
                    'form': hero_form,
                    'imagebase': imagebase,
                    'title': 'Hero Skill Times',
                }
            )
    else:
        hero_form = HeroPlayerSkillBarsForm
    return render(
        request,
        'heroes/form.html',
        {
            'form': hero_form,
            'title': 'Hero Skill Times',
        }
    )


def hero_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        heroes = Hero.objects.filter(name__icontains=q, visible=True)[:20]
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
        hero = Hero.objects.get(name=hero_name)
        game_modes = GameMode.objects.filter(is_competitive=True)
        game_mode_list = [gm.steam_id for gm in game_modes]
        image = HeroPerformanceChart(
            hero=hero.steam_id,
            player=None,
            game_mode_list=game_mode_list,
            x_var=x_var,
            y_var=y_var,
            group_var=group_var,
            split_var=split_var,
            width=350,
            height=350
        )
        imagebase = basename(image.name)
        response_data = {}
        response_data['result'] = 'success'
        response_data['url'] = settings.MEDIA_URL+imagebase
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    else:
        data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)


def ability_detail(request, hero_name, ability_name):
    if ability_name == 'stats':
        ability = get_object_or_404(
            Ability,
            machine_name=ability_name,
        )
    else:
        ability = get_object_or_404(
            Ability,
            machine_name=ability_name,
            hero__machine_name=hero_name,
        )
    charts = []
    return render(
        request,
        'heroes/ability.html',
        {
            'ability': ability,
            'charts': charts,
        }
    )
