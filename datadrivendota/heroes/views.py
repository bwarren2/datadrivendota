from os.path import basename
import json
from functools import wraps


from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify
from utils.exceptions import NoDataFound

from datadrivendota.views import FormView
from matches.models import GameMode
from .json_data import (
    hero_vitals_json,
    hero_lineup_json,
    hero_performance_json,
    hero_progression_json,
    hero_performance_chart_json,
    hero_skillbuild_winrate_json,
    update_player_winrate,
)
from .models import Hero, Ability, HeroDossier, Role

from .forms import (
    HeroVitalsMultiSelect,
    HeroLineupMultiSelect,
    HeroPlayerPerformance,
    HeroPlayerSkillBarsForm,
    HeroProgressionForm,
    HeroBuildForm,
)

from utils.file_management import outsourceJson

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


def detail(request, hero_name):
    hero_slug = slugify(hero_name)
    current_hero = get_object_or_404(Hero, machine_name=hero_slug)
    abilities = Ability.objects.filter(
        is_core=True,
        hero=current_hero).order_by('steam_id')
    dossier = HeroDossier.objects.get(hero=current_hero)

    datalist, params = update_player_winrate(
        current_hero.steam_id,
        game_modes=[1, 2, 3, 4, 5],
    )
    params['outerWidth'] = 300
    params['outerHeight'] = 300
    params['margin']['left'] = 33
    json_data = outsourceJson(datalist, params)
    return render(
        request,
        'heroes/detail.html',
        {
            'hero': current_hero,
            'abilities': abilities,
            'dossier': dossier,
            'player_json': basename(json_data.name),
        }
    )

class Vitals(FormView):
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
    form = HeroVitalsMultiSelect
    attrs = [
        'heroes',
        'stats',
    ]
    json_function = staticmethod(hero_vitals_json)
    title = "Hero Vitals"
    html = "heroes/form.html"

    def amend_params(self, params):
        return params


class Lineup(FormView):
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
    form = HeroLineupMultiSelect
    attrs = [
        'heroes',
        'stat',
        'level',
    ]
    json_function = staticmethod(hero_lineup_json)
    title = "Hero Lineups"
    html = "heroes/form.html"

    def amend_params(self, params):
        params['draw_legend'] = True
        params['legendWidthPercent'] = .7
        params['legendHeightPercent'] = .1
        return params


#@devserver_profile(follow=[hero_performance_json])
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
            datalist, params = hero_performance_chart_json(
                hero=hero_form.cleaned_data['hero'],
                player=hero_form.cleaned_data['player'],
                game_mode_list=hero_form.cleaned_data['game_modes'],
                x_var=hero_form.cleaned_data['x_var'],
                y_var=hero_form.cleaned_data['y_var'],
                group_var=hero_form.cleaned_data['group_var'],
                split_var=hero_form.cleaned_data['split_var'],
            )
            json_data = outsourceJson(datalist, params)
            return render(
                request,
                'heroes/form.html',
                {
                    'form': hero_form,
                    'json_data': basename(json_data.name),
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


class HeroSkillProgression(FormView):
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
    form = HeroProgressionForm
    attrs = [
        'hero',
        'player',
        'game_modes',
        'division',
    ]
    json_function = staticmethod(hero_progression_json)
    title = "Hero Skilling"
    html = "heroes/form.html"

    def amend_params(self, params):
        params['path_stroke_width'] = 1
        return params


class HeroBuildLevel(FormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts skill usage for a player on a hero at certain levels."
        },
        ]
    form = HeroBuildForm
    attrs = [
        'hero',
        'player',
        'game_modes',
        'levels',
    ]
    json_function = staticmethod(hero_skillbuild_winrate_json)
    title = "SkillBuilld Winrate"
    html = "heroes/form.html"

    def amend_params(self, params):
        return params




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
        datalist, params = hero_performance_chart_json(
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
        json_data = outsourceJson(datalist, params)
        response_data = {}
        response_data['result'] = 'success'
        response_data['url'] = settings.MEDIA_URL+basename(json_data).name
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
