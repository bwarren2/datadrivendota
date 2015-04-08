import datetime
import json
from functools import wraps
from itertools import chain
from time import mktime

from django.http import HttpResponse
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.shortcuts import render
from django.conf import settings
from django.views.generic.edit import FormView

from utils.views import cast_dict, ability_infodict
from utils.pagination import SmarterPaginator
from heroes.models import Hero, Role
from .models import Match, PlayerMatchSummary, PickBan
from .forms import ContextSelect
from .mixins import (
    EndgameMixin,
    OwnTeamEndgameMixin,
    SameTeamEndgameMixin,
    ProgressionListMixin,
    AbilityBuildMixin,
    MatchParameterMixin,
    SingleMatchParameterMixin,
    RoleMixin,
    SetProgressionMixin,
)
from datadrivendota.views import ChartFormView, ApiView
from datadrivendota.forms import FollowMatchForm
from players.models import Player
from accounts.models import request_to_player

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
        if summary.leaver.steam_id != 0:
            summary.improper_player = True
        if summary.is_win:
            summary.won = True
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(
        match.start_time
    ).strftime('%H:%M:%S %Y-%m-%d')

    radiant_summaries = [
        summary for summary in summaries if summary.which_side() == 'Radiant'
    ]
    radiant_infodict = {}
    radiant_cast_list = []
    min_skill_length = 10  # Check if a row lacks data, aka things are borked.
    for summary in radiant_summaries:
        radiant_cast_list.append(cast_dict(summary))
        radiant_infodict[summary.player_slot] = ability_infodict(summary)
        min_skill_length = min(
            min_skill_length,
            len(radiant_infodict[summary.player_slot]['ability_dict'])
        )
    dire_summaries = [
        summary for summary in summaries if summary.which_side() == 'Dire'
    ]
    dire_infodict = {}
    dire_cast_list = []
    for summary in dire_summaries:
        dire_cast_list.append(cast_dict(summary))
        dire_infodict[summary.player_slot] = ability_infodict(summary)
        min_skill_length = min(
            min_skill_length,
            len(dire_infodict[summary.player_slot]['ability_dict'])
        )

    # Identify any pickbans for templating.
    try:
        # Magic numbers are bad, but 0 = radiant.  Fix later
        dire_picks = PickBan.objects.filter(
            match=match,
            team=1,
            is_pick=True
        ).select_related('hero')

        dire_bans = PickBan.objects.filter(
            match=match,
            team=1,
            is_pick=False
        ).select_related('hero')

        radiant_picks = PickBan.objects.filter(
            match=match,
            is_pick=True
        ).exclude(team=1).select_related('hero')

        radiant_bans = PickBan.objects.filter(
            match=match,
            is_pick=False
        ).exclude(team=1).select_related('hero')

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
                'radiant_cast_list': radiant_cast_list,
                'dire_cast_list': dire_cast_list,
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
                'radiant_cast_list': radiant_cast_list,
                'dire_cast_list': dire_cast_list,
                'radiant_infodict': radiant_infodict,
                'dire_infodict': dire_infodict,
                'min_skill_length': min_skill_length,
            }
        )


@devserver_profile()
def parse_preview(request, match_id=787900748):
    try:
        match = Match.objects.get(steam_id=match_id)
    except Match.DoesNotExist:
        raise Http404
    summaries = PlayerMatchSummary.objects.filter(
        match=match
    ).select_related().order_by('player_slot')

    slot_dict = {
        0: '#7CD51B',  # 1f77b4', #Radiant #7CD51B
        1: '#7CD51B',  # 7EF6C6',
        2: '#7CD51B',  # 9A1D9B',
        3: '#7CD51B',  # ECF14C',
        4: '#7CD51B',  # DB7226',
        128: '#BA3B15',  # E890BA',
        129: '#BA3B15',  # 99B15F',
        130: '#BA3B15',  # 75D1E1',
        131: '#BA3B15',  # 147335',
        132: '#BA3B15',  # 906A2B', #Dire  #BA3B15
    }

    css_color_dict = {}
    for summary in summaries:
        summary.kda = summary.kills - summary.deaths + .5*summary.assists
        if summary.which_side() == 'Radiant':
            summary.is_radiant = True
        else:
            summary.is_dire = True
        if summary.leaver.steam_id != 0:
            summary.improper_player = True
        if summary.is_win:
            summary.won = True
        css_color_dict[
            summary.hero.internal_name
        ] = slot_dict[summary.player_slot]
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(
        match.start_time
    ).strftime('%H:%M:%S %Y-%m-%d')

    radiant_summaries = [
        summary for summary in summaries if summary.which_side() == 'Radiant'
    ]
    radiant_cast_list = []
    for summary in radiant_summaries:
        radiant_cast_list.append(cast_dict(summary))

    dire_summaries = [
        summary for summary in summaries if summary.which_side() == 'Dire'
    ]
    dire_cast_list = []
    for summary in dire_summaries:
        dire_cast_list.append(cast_dict(summary))

    return render(
        request,
        'matches/parse_preview.html',
        {
            'match': match,
            'summaries': summaries,
            'radiant_cast_list': radiant_cast_list,
            'dire_cast_list': dire_cast_list,
            'css_color_dict': css_color_dict,
            'slot_dict': slot_dict,
            'side_kills': 'replay_parse_json/'+str(match.steam_id)+'_kills.json',
            'side_creeps': 'replay_parse_json/'+str(match.steam_id)+'_creeps.json',
            'side_towers': 'replay_parse_json/'+str(match.steam_id)+'_towers.json',
            'hero_kills': 'replay_parse_json/'+str(match.steam_id)+'_kill_dmg.json',
            'hero_deaths': 'replay_parse_json/'+str(match.steam_id)+'_death_dmg.json',
            'hero_creeps': 'replay_parse_json/'+str(match.steam_id)+'_hero_creeps.json',
        }
    )


@devserver_profile()
def parse_match(request, match_id=787900748):
    try:
        match = Match.objects.get(steam_id=match_id)
    except Match.DoesNotExist:
        raise Http404
    summaries = PlayerMatchSummary.objects.filter(
        match=match
    ).select_related().order_by('player_slot')

    slot_dict = {
        0: '#7CD51B',  # 1f77b4', #Radiant #7CD51B
        1: '#7CD51B',  # 7EF6C6',
        2: '#7CD51B',  # 9A1D9B',
        3: '#7CD51B',  # ECF14C',
        4: '#7CD51B',  # DB7226',
        128: '#BA3B15',  # E890BA',
        129: '#BA3B15',  # 99B15F',
        130: '#BA3B15',  # 75D1E1',
        131: '#BA3B15',  # 147335',
        132: '#BA3B15',  # 906A2B', #Dire  #BA3B15
    }

    css_color_dict = {}
    for summary in summaries:
        summary.kda = summary.kills - summary.deaths + .5*summary.assists
        if summary.which_side() == 'Radiant':
            summary.is_radiant = True
        else:
            summary.is_dire = True
        if summary.leaver.steam_id != 0:
            summary.improper_player = True
        if summary.is_win:
            summary.won = True
        css_color_dict[
            summary.hero.internal_name
        ] = slot_dict[summary.player_slot]
    match.hms_duration = datetime.timedelta(seconds=match.duration)
    match.hms_start_time = datetime.datetime.fromtimestamp(
        match.start_time
    ).strftime('%H:%M:%S %Y-%m-%d')

    radiant_summaries = [
        summary for summary in summaries if summary.which_side() == 'Radiant'
    ]
    radiant_cast_list = []
    for summary in radiant_summaries:
        radiant_cast_list.append(cast_dict(summary))

    dire_summaries = [
        summary for summary in summaries if summary.which_side() == 'Dire'
    ]
    dire_cast_list = []
    for summary in dire_summaries:
        dire_cast_list.append(cast_dict(summary))

    hero_id_names = {
        pms.hero.steam_id: pms.hero.internal_name
        for pms in summaries
    }

    return render(
        request,
        'matches/parse_match.html',
        {
            'match': match,
            'summaries': summaries,
            'radiant_cast_list': radiant_cast_list,
            'dire_cast_list': dire_cast_list,
            'css_color_dict': css_color_dict,
            'slot_dict': slot_dict,
            'hero_json': json.dumps(hero_id_names),
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

            page = request.GET.get('page')
            paginator = SmarterPaginator(
                object_list=match_list,
                per_page=results_per_page,
                current_page=page
            )
            match_list = paginator.current_page

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

            page = request.GET.get('page')
            paginator = SmarterPaginator(
                object_list=match_list,
                per_page=results_per_page,
                current_page=page
            )
            match_list = paginator.current_page

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

            page = request.GET.get('page')
            paginator = SmarterPaginator(
                object_list=match_list,
                per_page=results_per_page,
                current_page=page
            )
            match_list = paginator.current_page

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


class MatchHeroContext(FormView):
    template_name = 'matches/match_hero_context.html'
    form_class = ContextSelect

    def get(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)

        if form.is_valid():
            return self.form_valid(form)

        else:
            return self.form_invalid(form)
            return render(
                self.request,
                self.template_name,
                {'form': form_class()},
            )

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })

        if self.request.method in ('GET'):
            kwargs.update({
                'data': self.request.GET,
                'files': self.request.FILES,
            })

        return kwargs

    def form_valid(self, form):
        hero = form.cleaned_data['hero']

        hero_obj = Hero.objects.get(steam_id=hero)

        hero_name = hero_obj.name
        machine_name = hero_obj.machine_name
        matches = ",".join(str(x) for x in form.cleaned_data['matches'])
        outcome = form.cleaned_data['outcome']
        amendments = {
            'form': form,
            'hero': hero,
            'matches': matches,
            'outcome': outcome,
            'hero_name': hero_name,
            'machine_name': machine_name,
        }
        return render(
            self.request,
            self.template_name,
            self.get_context_data(**amendments),
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

class ProgressionSet(SetProgressionMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts level progression data for a specific hero in specific matches."
        }
    ]
    title = "Match Set Hero Progression"
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
            if pms.match.radiant_team is not None:
                match_data[id]['match_data']['Radiant']['team'] = pms.match.radiant_team
            if pms.match.dire_team is not None:
                match_data[id]['match_data']['Dire']['team'] = pms.match.dire_team

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

class ApiSetProgressionChart(SetProgressionMixin, ApiView):
    pass
