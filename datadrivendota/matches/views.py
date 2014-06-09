import datetime
import json
from functools import wraps
from itertools import chain
from time import mktime

from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.conf import settings

from heroes.models import Hero, Role
from .models import Match, PlayerMatchSummary, PickBan, SkillBuild
from .mixins import (
    EndgameMixin,
    OwnTeamEndgameMixin,
    SameTeamEndgameMixin,
    ProgressionListMixin,
    AbilityBuildMixin,
    MatchParameterMixin,
    SingleMatchParameterMixin,
    RoleMixin,
)
from datadrivendota.views import ChartFormView, ApiView
from datadrivendota.forms import FollowMatchForm
from players.models import request_to_player, Player

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


@user_passes_test(lambda u: u.is_superuser)
@devserver_profile()
def overview(request):
    skill_levels = range(0, 4)
    match_info = {}
    validity_set = [Match.LEGIT, Match.UNCOUNTED, Match.UNPROCESSED]
    heroes = Hero.objects.filter(visible=True)
    for hero in heroes:
        match_info[hero] = {}
    for skill in skill_levels:
        match_info[hero][skill] = {}
        for validity in validity_set:
            match_info[hero][skill][validity] = PlayerMatchSummary.objects.\
                filter(
                    hero=hero,
                    match__validity=validity,
                    match__skill=skill
                ).count()

    return render(
        request,
        'matches/index.html',
        {
            'match_info': match_info,
            'skill_levels': skill_levels
        }
    )


@devserver_profile()
def match(request, match_id):
    try:
        match = Match.objects.get(steam_id=match_id)
    except Match.DoesNotExist:
        raise Http404
    summaries = PlayerMatchSummary.objects.filter(
        match=match
    ).select_related().order_by('player_slot')
    for summary in summaries:
        summary.kda = summary.kills - summary.deaths + .5*summary.assists
        if summary.which_side() == 'Radiant':
            summary.is_radiant = True
        else:
            summary.is_dire = True
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(
        match.start_time
    ).strftime('%H:%M:%S %Y-%m-%d')

    radiant_summaries = [
        summary for summary in summaries if summary.which_side() == 'Radiant'
    ]
    radiant_infodict = {}
    min_skill_length = 10  # Check if a row lacks data, aka things are borked.
    for summary in radiant_summaries:
        try:
            radiant_infodict[summary.player_slot] = {
                'hero_thumbshot': summary.hero.thumbshot,
                'hero_thumbshot_url': summary.hero.thumbshot.url,
                'hero_name': summary.hero.name,
                'hero_machine_name': summary.hero.machine_name,
                'ability_dict': [
                    {
                        'name': sb.ability.name,
                        'machine_name': sb.ability.machine_name,
                        'picture_url': sb.ability.picture.url
                    } for sb in SkillBuild.objects.filter(
                        player_match_summary=summary
                    ).select_related()
                ]
            }
        except ValueError:
            radiant_infodict[summary.player_slot] = {
                'hero_thumbshot': '',
                'hero_thumbshot_url': '',
                'hero_name': summary.hero.name,
                'hero_machine_name': summary.hero.machine_name,
                'ability_dict': [
                    {
                        'name': sb.ability.name,
                        'machine_name': sb.ability.machine_name,
                        'picture_url': sb.ability.picture.url
                    } for sb in SkillBuild.objects.filter(
                        player_match_summary=summary
                    ).select_related()
                ]
            }
        min_skill_length = min(
            min_skill_length,
            len(radiant_infodict[summary.player_slot]['ability_dict'])
        )
    dire_summaries = [
        summary for summary in summaries if summary.which_side() == 'Dire'
    ]
    dire_infodict = {}
    for summary in dire_summaries:
        try:
            dire_infodict[summary.player_slot] = {
                'hero_thumbshot': summary.hero.thumbshot,
                'hero_thumbshot_url': summary.hero.thumbshot.url,
                'hero_name': summary.hero.name,
                'hero_machine_name': summary.hero.machine_name,
                'ability_dict': [
                    {
                        'machine_name': sb.ability.machine_name,
                        'picture_url': sb.ability.picture.url
                    } for sb in SkillBuild.objects.filter(
                        player_match_summary=summary
                    ).select_related()
                ]
            }
        except ValueError:
            dire_infodict[summary.player_slot] = {
                'hero_thumbshot': '',
                'hero_thumbshot_url': '',
                'hero_name': summary.hero.name,
                'hero_machine_name': summary.hero.machine_name,
                'ability_dict': [
                    {
                        'machine_name': sb.ability.machine_name,
                        'picture_url': sb.ability.picture.url
                    } for sb in SkillBuild.objects.filter(
                        player_match_summary=summary
                    ).select_related()
                ]
            }
        min_skill_length = min(
            min_skill_length,
            len(dire_infodict[summary.player_slot]['ability_dict'])
        )

    #Identify any pickbans for templating.
    dire_hero_ids = [
        pms.hero.steam_id for pms in summaries if pms.which_side() == 'Dire'
    ]
    try:
        pick = [
            pickban for pickban in match.pickban_set.all() if pickban.is_pick
        ][0]
        if pick.hero.steam_id in dire_hero_ids:
            dire_flag = pick.team
        else:
            dire_flag = 1-pick.team

        dire_picks = PickBan.objects.filter(
            match=match,
            team=dire_flag,
            is_pick=True
        ).select_related()
        dire_bans = PickBan.objects.filter(
            match=match,
            team=dire_flag,
            is_pick=False
        ).select_related()
        radiant_picks = PickBan.objects.filter(
            match=match,
            is_pick=True
        ).exclude(team=dire_flag).select_related()
        radiant_bans = PickBan.objects.filter(
            match=match,
            is_pick=False
        ).exclude(team=dire_flag).select_related()

        pickban_length = (
            dire_picks.count() +
            dire_bans.count() +
            radiant_picks.count() +
            radiant_bans.count()
        )

        return render(
            request,
            'matches/detail.html',
            {
                'match': match,
                'summaries': summaries,
                'radiant_infodict': radiant_infodict,
                'dire_infodict': dire_infodict,
                'dire_picks': dire_picks,
                'radiant_picks': radiant_picks,
                'dire_bans': dire_bans,
                'radiant_bans': radiant_bans,
                'min_skill_length': min_skill_length,
                'pickban_length': pickban_length,
            }
        )
    except IndexError:
        return render(
            request,
            'matches/detail.html',
            {
                'match': match,
                'summaries': summaries,
                'radiant_infodict': radiant_infodict,
                'dire_infodict': dire_infodict,
                'min_skill_length': min_skill_length,
            }
        )


@devserver_profile(follow=[])
def follow_match_feed(request):
    results_per_page = 20
    total_results = 500

    #One of the default load methods, without the form.
    if request.method != 'POST':
        form = FollowMatchForm()
        try:
            player = request_to_player(request)
            follow_list = [
                follow for follow in player.userprofile.following.all()
            ]
            match_list = Match.objects.filter(
                validity=Match.LEGIT,
                playermatchsummary__player__in=follow_list
            )
            match_list = match_list.select_related()\
                .distinct().order_by('-start_time')[:total_results]

            paginator = Paginator(match_list, results_per_page)
            page = request.GET.get('page')
            try:
                match_list = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                match_list = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of
                # results.
                match_list = paginator.page(paginator.num_pages)

            pms_list = PlayerMatchSummary.\
                objects.filter(match__in=match_list)\
                .select_related().order_by('-match__start_time')[:500]
            match_data = annotated_matches(pms_list, follow_list)
            return render(
                request,
                'matches/follow.html',
                {
                    'form': form,
                    'match_list': match_list,
                    'match_data': match_data,
                }
            )

        except AttributeError:
            pro_list = Player.objects.exclude(pro_name=None)
            match_list = Match.objects.filter(
                validity=Match.LEGIT,
                playermatchsummary__player__in=pro_list
            )
            match_list = match_list.select_related()\
                .distinct().order_by('-start_time')[:total_results]

            paginator = Paginator(match_list, results_per_page)
            page = request.GET.get('page')
            try:
                match_list = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                match_list = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of
                # results.
                match_list = paginator.page(paginator.num_pages)

            pms_list = PlayerMatchSummary.\
                objects.filter(match__in=match_list).select_related()

            match_data = annotated_matches(pms_list, [])
            return render(
                request,
                'matches/follow.html',
                {
                    'form': form,
                    'match_list': match_list,
                    'match_data': match_data,
                }
            )
    #Using the form to submit
    else:
        form = FollowMatchForm(request.POST)
        if form.is_valid():
            match_list = Match.objects.filter(
                validity=Match.LEGIT,
            )
            if form.cleaned_data['hero'] is not None:
                match_list = match_list.filter(
                    playermatchsummary__hero__steam_id=
                    form.cleaned_data['hero'],
                )
            if form.cleaned_data['player'] is not None:
                match_list = match_list.filter(
                    playermatchsummary__player__steam_id=
                    form.cleaned_data['player'],
                )
            if form.cleaned_data['min_date'] is not None:
                min_date_utc = mktime(
                    form.cleaned_data['min_date'].timetuple()
                    )
                match_list = match_list.filter(
                    start_time__gte=min_date_utc,
                )
            if form.cleaned_data['max_date'] is not None:
                max_date_utc = mktime(
                    form.cleaned_data['max_date'].timetuple()
                    )
                match_list = match_list.filter(
                    start_time__lte=max_date_utc,
                )

            match_list = match_list.select_related()\
                .distinct().order_by('-start_time')[:total_results]

            paginator = Paginator(match_list, results_per_page)
            page = request.GET.get('page')
            try:
                match_list = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                match_list = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of
                # results.
                match_list = paginator.page(paginator.num_pages)

            pms_list = PlayerMatchSummary.\
                objects.filter(match__in=match_list).select_related()

            match_data = annotated_matches(pms_list, [])
            return render(
                request,
                'matches/follow.html',
                {
                    'form': form,
                    'match_list': match_list,
                    'match_data': match_data,
                }
            )
        else:
            return render(
                request,
                'matches/follow.html',
                {
                    'form': form,
                }
            )


class MatchParameterChart(MatchParameterMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page scatterplots end-of-game data for a match of your choice."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare kills and hero damage to see who was killstealing in a match, or hero damage and gold to see who was producing a return on investment."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and match you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for teams, try other tabs.",
            'placement': "bottom"
        },
    ]
    title = "Match Parameter Scatter"
    html = "matches/form.html"


class Endgame(EndgameMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for players of your choosing."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare kills-deaths+assists/2 (KDA2, kind of a net score) between imported players."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and players you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for teams, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: how do [A]kke's and Funn1k's KDA2s change based on win/loss?  Hint: tweak the group and split vars for different renderings."
        }
    ]
    title = "Endgame Charts"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class OwnTeamEndgame(OwnTeamEndgameMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for teams for each player of your choosing."
        }
    ]
    title = "Own-Team Endgame Charts"
    html = "matches/form.html"



class SameTeamEndgame(SameTeamEndgameMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for groups of players."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare team kills to team assists for any game with the given players on the same team."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which attributes and players you want to render here."
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for individuals, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: When Funn1k, Dendi, and XBOCT play together, what KDA2 does their team exceed when they win?"
        }
    ]
    title = "Same Team Endgame Charts"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class ProgressionList(ProgressionListMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts level progression data for specific players in specific matches."
        }
    ]
    title = "Match List Hero Progression"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class AbilityBuild(AbilityBuildMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page is one of the few to chart within-game data: it plots when people place skill points in a game, with the first point placement being 0 minutes."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can see how people leveled in game with Dendi on Magnus (550709502)."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Specify which match id you want and output formatting here."
        },
        {
            'orphan': True,
            'title': "Important note!",
            'content': "This only works for games we have imported!  The data management page lets qualified users add players to the import process."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For the overview for a player, try players:index.  For the match overview, try /matches/<match-id>",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: in match 550709502, who slowed down when?  When did Slark and Lifesteal crush their enemies?"
        }
    ]
    title = "Match Ability Breakdown"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


def annotated_matches(pms_list, follow_list):
    match_data = {}

    for pms in pms_list:
        id = pms.match.steam_id
        side = pms.which_side()
        if pms.match.steam_id not in match_data.keys():
            match_data[id] = {}
            match_data[id]['pms_data'] = {}
            match_data[id]['pms_data']['Radiant'] = {}
            match_data[id]['pms_data']['Dire'] = {}
            match_data[id]['match_data'] = {}
            match_data[id]['match_data']['Radiant'] = {}
            match_data[id]['match_data']['Radiant']['is_win'] = False
            match_data[id]['match_data']['Radiant']['kills'] = 0
            match_data[id]['match_data']['Radiant']['deaths'] = 0
            match_data[id]['match_data']['Radiant']['assists'] = 0
            match_data[id]['match_data']['Radiant']['KDA2'] = 0
            match_data[id]['match_data']['Dire'] = {}
            match_data[id]['match_data']['Dire']['is_win'] = False
            match_data[id]['match_data']['Dire']['kills'] = 0
            match_data[id]['match_data']['Dire']['deaths'] = 0
            match_data[id]['match_data']['Dire']['assists'] = 0
            match_data[id]['match_data']['Dire']['KDA2'] = 0

        match_data[id]['match_data']['display_date'] = \
            datetime.datetime.fromtimestamp(pms.match.start_time)

        match_data[id]['match_data']['display_duration'] = \
            str(datetime.timedelta(seconds=pms.match.duration))

        match_data[id]['match_data']['game_mode'] = \
            pms.match.game_mode.description

        if pms.is_win:
            match_data[id]['match_data'][side]['is_win'] = True

        match_data[id]['match_data']['id'] = id

        match_data[id]['match_data'][side]['kills'] += pms.kills
        match_data[id]['match_data'][side]['deaths'] += pms.deaths
        match_data[id]['match_data'][side]['assists'] += pms.assists
        match_data[id]['match_data'][side]['KDA2'] += pms.kills\
            - pms.deaths + pms.assists/2.0

        pms_data = {}
        try:
            pms_data['hero_image'] = pms.hero.thumbshot.url
        except ValueError:
            pms_data['hero_image'] = None
        pms_data['hero_name'] = pms.hero.name
        pms_data['player_slot'] = pms.player_slot
        pms_data['side'] = side
        pms_data['kills'] = pms.kills
        pms_data['deaths'] = pms.deaths
        pms_data['assists'] = pms.assists
        pms_data['KDA2'] = \
            pms.kills - pms.deaths + pms.assists / 2.0
        if pms.player.avatar is not None:
            pms_data['player_image'] = pms.player.avatar
            pms_data['player_name'] = pms.player.persona_name
        if pms.player in follow_list:
            pms_data['followed'] = True

        match_data[id]['pms_data'][side][pms.player_slot] = pms_data

    match_list = []
    for key in sorted(match_data.iterkeys(), reverse=True):
        match_list.append(match_data[key])
    return match_list


def match_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        matches = Match.objects.filter(steam_id__icontains=q)[:20]
        results = []
        for i, match in enumerate(matches):
            match_json = {}
            match_json['id'] = i
            match_json['label'] = "{0}".format(match.steam_id)
            match_json['value'] = "{0}".format(match.steam_id)
            results.append(match_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def combobox_tags(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        heroes = [h.name for h in Hero.objects.filter(name__icontains=q)[:5]]
        alignments = ['Strength', 'Agility', 'Intelligence']
        matched_alignments = [s for s in alignments if q.lower() in s.lower()]
        roles = [r.name for r in Role.objects.filter(name__icontains=q)[:5]]
        results = []
        for i, string in enumerate(chain(heroes, matched_alignments, roles)):
            match_json = {}
            match_json['id'] = i
            match_json['label'] = string
            match_json['value'] = string
            results.append(match_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


class ApiEndgameChart(EndgameMixin, ApiView):
    pass


class ApiOwnTeamEndgameChart(OwnTeamEndgameMixin, ApiView):
    pass


class ApiSameTeamEndgameChart(SameTeamEndgameMixin, ApiView):
    pass


class ApiProgressionListChart(ProgressionListMixin, ApiView):
    pass


class ApiAbilityBuildChart(AbilityBuildMixin, ApiView):
    pass


class ApiMatchScatterChart(MatchParameterMixin, ApiView):
    pass


class ApiMatchBarChart(SingleMatchParameterMixin, ApiView):
    pass


class ApiRoleChart(RoleMixin, ApiView):
    pass
