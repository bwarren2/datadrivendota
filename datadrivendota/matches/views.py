import datetime
import json
from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from os.path import basename
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.conf import settings
from heroes.models import Hero
from .forms import (
    EndgameSelect,
    TeamEndgameSelect,
    MatchAbilitySelect,
    MatchListSelect
)
from .models import Match, PlayerMatchSummary, PickBan
from .json_data import (
    player_endgame_json,
    team_endgame_json,
    match_ability_json,
    match_list_json,
    match_parameter_json,
    player_team_endgame_json,
    single_match_parameter_json,
    match_role_json
)
from datadrivendota.views import FormView
from players.models import request_to_player, Player
from utils.exceptions import NoDataFound
from django.core.urlresolvers import reverse
from utils.file_management import outsourceJson

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
        match = Match.objects.select_related().get(steam_id=match_id)
    except Match.DoesNotExist:
        raise Http404
    summaries = PlayerMatchSummary.objects.filter(
        match=match
    ).select_related().order_by('player_slot')
    for summary in summaries:
        summary.kda = summary.kills - summary.deaths + .5*summary.assists
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(
        match.start_time
    ).strftime('%H:%M:%S %Y-%m-%d')

    try:
        datalist, params = match_parameter_json(
            match_id,
            'kills',
            'hero_damage'
        )
        params['outerWidth'] = 225
        params['outerHeight'] = 225
        kill_dmg_json_name = basename(outsourceJson(datalist, params).name)
    except NoDataFound:
        kill_dmg_json_name = None

    try:
        datalist, params = match_parameter_json(
            match_id,
            'gold_per_min',
            'xp_per_min'
        )
        params['outerWidth'] = 225
        params['outerHeight'] = 225
        xp_gold_json = outsourceJson(datalist,  params)
    except NoDataFound:
        xp_gold_json = None

    try:
        xp_gold_json_name = basename(xp_gold_json.name)
    except AttributeError:
        xp_gold_json_name = None

    try:
        datalist, params = match_ability_json(
            match=match_id,
            split_var='side'
            )
        params['outerWidth'] = 225
        params['outerHeight'] = 225
        abilities = outsourceJson(datalist, params)
    except NoDataFound:
        abilities = None

    try:
        datalist, params = match_role_json(
            match_id,
        )
        params['outerWidth'] = 225
        params['outerHeight'] = 225
        params['draw_legend'] = False
        roles_json_name = basename(outsourceJson(datalist, params).name)
    except NoDataFound:
        roles_json_name = None

    try:
        datalist, params = single_match_parameter_json(
            match_id, 'tower_damage',
            title='Tower Damage',
        )
        params['outerWidth'] = 375
        params['outerHeight'] = 250
        tower_damage_json_name = basename(outsourceJson(datalist, params).name)
    except NoDataFound:
        tower_damage_json_name = None

    try:
        datalist, params = single_match_parameter_json(
            match_id, 'last_hits',
            title='Last Hits',
        )
        params['outerWidth'] = 375
        params['outerHeight'] = 250
        last_hits_json_name = basename(outsourceJson(datalist, params).name)
    except NoDataFound:
        last_hits_json_name = None

    try:
        datalist, params = single_match_parameter_json(
            match_id, 'K-D+.5*A',
            title='K-D+.5*A (KDA2)',
        )
        params['outerWidth'] = 375
        params['outerHeight'] = 250
        kda_json_name = basename(outsourceJson(datalist, params).name)
    except NoDataFound:
        kda_json_name = None


    try:
        abilities_name = basename(abilities.name)
    except AttributeError:
        abilities_name = None

    radiant_summaries = [
        summary for summary in summaries if summary.which_side() == 'Radiant'
    ]
    dire_summaries = [
        summary for summary in summaries if summary.which_side() == 'Dire'
    ]

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

        return render(
            request,
            'matches/detail.html',
            {
                'match': match,
                'summaries': summaries,
                'radiant_summaries': radiant_summaries,
                'dire_summaries': dire_summaries,
                'kill_dmg_json': kill_dmg_json_name,
                'xp_gold_json': xp_gold_json_name,
                'abilities_json': abilities_name,
                'dire_picks': dire_picks,
                'radiant_picks': radiant_picks,
                'dire_bans': dire_bans,
                'radiant_bans': radiant_bans,
                'tower_damage_json': tower_damage_json_name,
                'last_hits_json': last_hits_json_name,
                'roles_json': roles_json_name,
                'kda_json': kda_json_name,
            }
        )
    except IndexError:
        return render(
            request,
            'matches/detail.html',
            {
                'match': match,
                'summaries': summaries,
                'radiant_summaries': radiant_summaries,
                'dire_summaries': dire_summaries,
                'kill_dmg_json': kill_dmg_json_name,
                'xp_gold_json': xp_gold_json_name,
                'abilities_json': abilities_name,
                'tower_damage_json': tower_damage_json_name,
                'last_hits_json': last_hits_json_name,
                'roles_json': roles_json_name,
                'kda_json': kda_json_name,
            }
        )


@devserver_profile(follow=[])
def follow_match_feed(request):

    mode = request.GET.get('format', 'lineup_thumbs')
    try:
        player = request_to_player(request)
        follow_list = [follow for follow in player.userprofile.following.all()]
        match_list = Match.objects.filter(
            validity=Match.LEGIT,
            playermatchsummary__player__in=follow_list
        )
        match_list = match_list.select_related()\
            .distinct().order_by('-start_time')[:500]

        paginator = Paginator(match_list, 20)
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
        print match_data
        return render(
            request,
            'matches/follow.html',
            {
                'match_list': match_list,
                'match_data': match_data,
                mode: 'true'
            }
        )

    except AttributeError:
        pro_list = Player.objects.exclude(pro_name=None)
        match_list = Match.objects.filter(
            validity=Match.LEGIT,
            playermatchsummary__player__in=pro_list
        )
        match_list = match_list.select_related()\
            .distinct().order_by('-start_time')[:500]

        paginator = Paginator(match_list, 20)
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
        print match_data
        return render(
            request,
            'matches/follow.html',
            {
                'match_list': match_list,
                'match_data': match_data,
                mode: 'true'
            }
        )


class Endgame(FormView):
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
    form = EndgameSelect
    attrs = [
        'players',
        'game_modes',
        'x_var',
        'y_var',
        'split_var',
        'group_var',
    ]
    json_function = staticmethod(player_endgame_json)
    title = "Endgame Charts"
    html = "matches/form.html"

    def amend_params(self, params):
        return params


class OwnTeamEndgame(FormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts end-of-game data for teams for each player of your choosing."
        }
    ]
    form = EndgameSelect
    attrs = [
        'players',
        'game_modes',
        'x_var',
        'y_var',
        'split_var',
        'group_var',
    ]
    json_function = staticmethod(player_team_endgame_json)
    title = "Own-Team Endgame Charts"
    html = "matches/form.html"


class SameTeamEndgame(FormView):
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
    form = TeamEndgameSelect
    attrs = [
        'players',
        'game_modes',
        'x_var',
        'y_var',
        'split_var',
        'group_var',
        'compressor',
    ]
    json_function = staticmethod(team_endgame_json)
    title = "Same Team Endgame Charts"
    html = "matches/form.html"

    def amend_params(self, params):
        return params

class ProgressionList(FormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts level progression data for specific players in specific matches."
        }
    ]
    form = MatchListSelect
    attrs = [
        'match_list',
        'player_list',
    ]
    json_function = staticmethod(match_list_json)
    title = "Match List Hero Progression"
    html = "matches/form.html"

    def amend_params(self, params):
        return params

class AbilityBuild(FormView):
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
    form = MatchAbilitySelect
    attrs = [
        'match',
        'split_var',
    ]
    json_function = staticmethod(match_ability_json)
    title = "Match Ability Breakdown"
    html = "matches/form.html"

    def amend_params(self, params):
        return params
    def extra_data(self):
        match_url = reverse(
            'matches:match_detail',
            kwargs={'match_id': select_form.cleaned_data['match']}
        )
        extra_notes = "<a href='{0}'>See this match</a>".format(
            match_url
        )

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
            match_data[id]['match_data']['Radiant']['Kills'] = 0
            match_data[id]['match_data']['Radiant']['Deaths'] = 0
            match_data[id]['match_data']['Radiant']['Assists'] = 0
            match_data[id]['match_data']['Radiant']['KDA2'] = 0
            match_data[id]['match_data']['Dire'] = {}
            match_data[id]['match_data']['Dire']['Kills'] = 0
            match_data[id]['match_data']['Dire']['Deaths'] = 0
            match_data[id]['match_data']['Dire']['Assists'] = 0
            match_data[id]['match_data']['Dire']['KDA2'] = 0

        match_data[id]['match_data']['display_date'] = \
            datetime.datetime.fromtimestamp(pms.match.start_time)

        match_data[id]['match_data']['display_duration'] = \
            str(datetime.timedelta(seconds=pms.match.duration))

        match_data[id]['match_data']['game_mode'] = \
            pms.match.game_mode.description

        match_data[id]['match_data']['id'] = id

        match_data[id]['match_data'][side]['Kills'] += pms.kills
        match_data[id]['match_data'][side]['Deaths'] += pms.deaths
        match_data[id]['match_data'][side]['Assists'] += pms.assists
        match_data[id]['match_data'][side]['KDA2'] += pms.kills\
            - pms.deaths + pms.assists/2

        pms_data = {}
        try:
            pms_data['hero_image'] = pms.hero.thumbshot.url
        except ValueError:
            pms_data['hero_image'] = None
        pms_data['hero_name'] = pms.hero.name
        pms_data['player_slot'] = pms.player_slot
        pms_data['side'] = side
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
    print match_list
    return match_list


def match_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        matches = Match.objects.filter(steam_id__icontains=q)[:20]
        results = []
        print q, matches
        for i, match in enumerate(matches):
            match_json = {}
            match_json['id'] = i
            match_json['label'] = "M#: {0}".format(match.steam_id)
            match_json['value'] = "M#: {0}".format(match.steam_id)
            results.append(match_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
