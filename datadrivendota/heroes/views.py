from os.path import basename
import json
from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.utils.text import slugify

from datadrivendota.views import ChartFormView, ApiView
from utils.file_management import moveJson

from matches.models import GameMode
from .json_data import (
    update_player_winrate,
)
from .models import Hero, Ability, HeroDossier, Role, Assignment
from .mixins import (
    VitalsMixin,
    LineupMixin,
    HeroPerformanceMixin,
    HeroSkillProgressionMixin,
    HeroBuildLevelMixin,
    UpdatePlayerWinrateMixin,
    HeroPerformanceLineupMixin,
    HeroPickRateMixin,
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
    hero_list = Hero.objects.filter(visible=True).order_by('name')
    role_list = Role.objects.all()
    assignments = Assignment.objects.all().select_related()
    dictAssignments = {}
    for a in assignments:
        if a.hero.name not in dictAssignments:
            dictAssignments[a.hero.name] = []
        dictAssignments[a.hero.name].append(a.role.name)

    for hero in hero_list:
        try:
            hero.classes = " ".join(dictAssignments[hero.name])
        #Some annoying people, like Abaddon, lack assignments.
        except KeyError:
            hero.classes = ''
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
    return render(
        request,
        'heroes/detail.html',
        {
            'hero': current_hero,
            'abilities': abilities,
            'dossier': dossier,
        }
    )


class Vitals(VitalsMixin, ChartFormView):
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
    title = "Hero Vitals"
    html = "heroes/form.html"

    def amend_params(self, chart):
        return chart


class Lineup(LineupMixin, ChartFormView):
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
    title = "Hero Lineups"
    html = "heroes/form.html"

    def amend_params(self, chart):
        chart.params.draw_legend = True
        chart.params.legendWidthPercent = .7
        chart.params.legendHeightPercent = .1
        return chart


class HeroPerformance(HeroPerformanceMixin, ChartFormView):
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
            'content': "Valve automagically determines their own skill bracketing, with 1-2-3 being normal-high-very high."
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
    title = "Hero Performance"
    html = "heroes/form.html"

    def amend_params(self, chart):
        chart.params.draw_legend = True
        chart.params.legendWidthPercent = .7
        chart.params.legendHeightPercent = .1
        return chart


class HeroSkillProgression(HeroSkillProgressionMixin, ChartFormView):
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
            'content': "For example, you can see how quickly very-high skill Anti-Mage players farm compared to normal skill ones, and include your own data (if you are being imported)."
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
            'content': "The skill designation is given automagically by Valve; 1-2-3 correspond to normal-high-very high."
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
            'content': "Challenge: for your favorite hero, how many more levels can high-skill players have over normal skill players at the 30 minute mark?"
        }
    ]
    title = "Hero Skilling"
    html = "heroes/form.html"

    def amend_params(self, chart):
        chart.params.path_stroke_width = 2
        return chart


class HeroBuildLevel(HeroBuildLevelMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts skill usage for a player on a hero at certain levels."
        },
        ]
    title = "SkillBuild Winrate"
    html = "heroes/form.html"


class HeroPerformanceLineup(HeroPerformanceLineupMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts a stat across all heroes, in games of a skill level."
        },
        ]
    title = "Hero Performance Lineup"
    html = "heroes/form.html"

class HeroPickBanLineup(HeroPickRateMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts a stat across all heroes, in games of a skill level."
        },
        ]
    title = "Hero Performance Lineup"
    html = "heroes/form.html"


def hero_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        heroes = Hero.objects.filter(name__icontains=q, visible=True)[:20]
        results = []
        for hero in heroes:
            hero_json = {}
            hero_json['id'] = hero.steam_id
            hero_json['label'] = hero.name
            hero_json['value'] = hero.steam_id
            results.append(hero_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


#API endpoints
class ApiVitalsChart(VitalsMixin, ApiView):
    pass


class ApiLineupChart(LineupMixin, ApiView):
    pass


class ApiHeroPerformanceChart(HeroPerformanceMixin, ApiView):
    pass


class ApiSkillProgressionChart(HeroSkillProgressionMixin, ApiView):
    pass


class ApiBuildLevelChart(HeroBuildLevelMixin, ApiView):
    pass


class ApiUpdatePlayerWinrateChart(UpdatePlayerWinrateMixin, ApiView):
    pass


class ApiHeroPerformanceLineupChart(HeroPerformanceLineupMixin, ApiView):
    pass


def ability_detail(request, ability_name):
    if ability_name == 'stats':
        ability = get_object_or_404(
            Ability,
            machine_name=ability_name,
        )
    else:
        ability = get_object_or_404(
            Ability,
            machine_name=ability_name,
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
