import datetime
from django.contrib.auth.decorators import user_passes_test
from functools import wraps
from os.path import basename
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth.decorators import permission_required
from heroes.models import Hero
from .forms import EndgameSelect, TeamEndgameSelect, MatchAbilitySelect
from .r import EndgameChart, MatchParameterScatterplot
from .models import Match, PlayerMatchSummary, PickBan
from .json_data import (
    player_endgame_json,
    team_endgame_json,
    match_ability_json,
    match_parameter_json
)
from players.models import request_to_player
from utils.exceptions import NoDataFound
from django.core.urlresolvers import reverse

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


@permission_required('players.can_look')
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
    kill_dmg_json = match_parameter_json(
        match_id,
        'kills',
        'hero_damage'
    )
    xp_gold_json = match_parameter_json(
        match_id,
        'gold_per_min',
        'xp_per_min'
    )
    abilities = match_ability_json(
        match_id=match_id,
        width=250,
        height=250,
        split_var='side'
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

        return render(
            request,
            'matches/detail.html',
            {
                'match': match,
                'summaries': summaries,
                'kill_dmg_json': basename(kill_dmg_json.name),
                'xp_gold_json': basename(xp_gold_json.name),
                'abilities_json': basename(abilities.name),
                'dire_picks': dire_picks,
                'radiant_picks': radiant_picks,
                'dire_bans': dire_bans,
                'radiant_bans': radiant_bans,
            }
        )
    except IndexError:
        return render(
            request,
            'matches/detail.html',
            {
                'match': match,
                'summaries': summaries,
                'kill_dmg_json': basename(kill_dmg_json.name),
                'xp_gold_json': basename(xp_gold_json.name),
                'abilities_json': basename(abilities.name),
            }
        )


@permission_required('players.can_look')
@devserver_profile(follow=[])
def follow_match_feed(request):

    player = request_to_player(request)
    if player is not None:
        follow_list = [follow for follow in player.userprofile.following.all()]
        match_list = Match.objects.filter(
            validity=Match.LEGIT,
            playermatchsummary__player__in=follow_list
        )
        match_list = match_list.select_related().distinct()[:500]

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

            match_data[id]['match_data']['display_date'] = \
                datetime.datetime.fromtimestamp(pms.match.start_time)

            match_data[id]['match_data']['display_duration'] = \
                str(datetime.timedelta(seconds=pms.match.duration))

            match_data[id]['match_data']['game_mode'] = \
                pms.match.game_mode.description

            pms_data = {}
            pms_data['hero_image'] = pms.hero.thumbshot.url
            pms_data['hero_name'] = pms.hero.name
            pms_data['player_slot'] = pms.player_slot
            pms_data['side'] = side
            pms_data['KDA2'] = \
                pms.kills - pms.deaths + pms.assists / 2.0
            if pms.player in follow_list:
                pms_data['player_image'] = pms.player.avatar
                pms_data['player_name'] = pms.player.persona_name
                pms_data['followed'] = True

            match_data[id]['pms_data'][side][pms.player_slot] = pms_data

        return render(
            request,
            'matches/follow.html',
            {
                'match_list': match_list,
                'match_data': match_data
            }
        )

    else:
        match_list = Match.objects.filter(validity=Match.LEGIT)[:100]

        paginator = Paginator(match_list, 10)
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

        for match in match_list:
            match.display_date = datetime.datetime.fromtimestamp(
                match.start_time
            )
            match.display_duration = str(datetime.timedelta(
                seconds=match.duration
            ))
        return render(
            request,
            'matches/index.html',
            {
                'match_list': match_list
            }
        )


@permission_required('players.can_touch')
@devserver_profile(follow=[EndgameChart])
def endgame(request):
    if request.GET:
        select_form = EndgameSelect(request.GET)
        if select_form.is_valid():
            try:
                json_data = player_endgame_json(
                    player_list=select_form.cleaned_data['players'],
                    mode_list=select_form.cleaned_data['game_modes'],
                    x_var=select_form.cleaned_data['x_var'],
                    y_var=select_form.cleaned_data['y_var'],
                    split_var=select_form.cleaned_data['split_var'],
                    group_var=select_form.cleaned_data['group_var']
                )

                return render(
                    request,
                    'matches/form.html',
                    {
                        'form': select_form,
                        'json_data': basename(json_data.name),
                        'title': 'Endgame Charts'
                    }
                )
            except NoDataFound:
                return render(
                    request,
                    'matches/form.html',
                    {
                        'form': select_form,
                        'error': 'error',
                        'title': 'Endgame Charts'
                    }
                )

    else:
        select_form = EndgameSelect()
    return render(
        request,
        'matches/form.html',
        {
            'form': select_form,
            'title': 'Endgame Charts'
        }
    )


@permission_required('players.can_touch')
@devserver_profile(follow=[team_endgame_json])
def team_endgame(request):
    if request.GET:
        select_form = TeamEndgameSelect(request.GET)
        if select_form.is_valid():
            try:
                json_data = team_endgame_json(
                    player_list=select_form.cleaned_data['players'],
                    mode_list=select_form.cleaned_data['game_modes'],
                    x_var=select_form.cleaned_data['x_var'],
                    y_var=select_form.cleaned_data['y_var'],
                    split_var=select_form.cleaned_data['split_var'],
                    group_var=select_form.cleaned_data['group_var'],
                    compressor=select_form.cleaned_data['compressor']
                )
                return render(
                    request,
                    'matches/form.html',
                    {
                        'form': select_form,
                        'json_data': basename(json_data.name),
                        'title': 'Endgame Charts'
                    }
                )

            except NoDataFound:
                return render(
                    request,
                    'matches/form.html',
                    {
                        'form': select_form,
                        'error': 'error',
                        'title': 'Endgame Charts'
                    }
                )
    else:
        select_form = TeamEndgameSelect()
    return render(
        request,
        'matches/form.html',
        {
            'form': select_form,
            'title': 'Endgame Charts'
        }
    )


@permission_required('players.can_touch')
@devserver_profile(follow=[match_ability_json])
def ability_build(request):
    title = 'Match Ability Breakdown'
    if request.GET:
        select_form = MatchAbilitySelect(request.GET)
        if select_form.is_valid():
            try:
                json_data = match_ability_json(
                    match_id=select_form.cleaned_data['match'],
                    split_var=select_form.cleaned_data['split_var']
                )
                match_url = reverse(
                    'matches:match_detail',
                    kwargs={'match_id': select_form.cleaned_data['match']}
                )
                extra_notes = "<a href='{0}'>See this match</a>".format(
                    match_url
                )
                return render(
                    request,
                    'matches/form.html',
                    {
                        'json_data': basename(json_data.name),
                        'title': title,
                        'form': select_form,
                        'extra_notes': extra_notes,
                    }
                )
            except NoDataFound:
                return render(
                    request,
                    'matches/form.html',
                    {
                        'error': 'error',
                        'title': title,
                        'form': select_form
                    }
                )
    else:
        select_form = MatchAbilitySelect()
    return render(
        request,
        'matches/form.html',
        {
            'form': select_form,
            'title': title,
        }
    )
