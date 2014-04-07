import datetime
import json
from celery import chain
from functools import wraps
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import permission_required
from os.path import basename
from .models import Player, UserProfile
from .r import CountWinrate, PlayerTimeline
from .forms import (
    PlayerWinrateLevers,
    PlayerTimelineForm,
    PlayerAddFollowForm,
    HeroAbilitiesForm,
    PlayerAdversarialForm,
)
from matches.models import PlayerMatchSummary, Match
from matches.management.tasks.valve_api_calls import (
    ApiContext,
    ValveApiCall,
    UpdatePlayerPersonas,
    AcquirePlayerData
)
from .models import request_to_player
from utils.exceptions import NoDataFound
from .json_data import (
    player_hero_side_json,
    player_winrate_json,
    player_hero_abilities_json,
    player_versus_winrate_json,
    )
from matches.json_data import player_endgame_json, player_team_endgame_json
from heroes.json_data import (
    hero_progression_json,
    hero_performance_chart_json
    )
from utils.file_management import outsourceJson
from heroes.models import Hero

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
    player_list = Player.objects.filter(updated=True)
    return render(
        request,
        'players/index.html',
        {
            'player_list': player_list
        }
    )


@permission_required('players.can_touch')
def followed_index(request):
    player_list = Player.objects.filter(updated=True)
    player_list = request.user.userprofile.following.all()
    return render(
        request,
        'players/index.html',
        {
            'player_list': player_list
        }
    )


def pro_index(request):
    player_list = Player.objects.exclude(pro_name=None)
    return render(
        request,
        'players/index.html',
        {
            'player_list': player_list
        }
    )


def detail(request, player_id=None):
    player = get_object_or_404(Player, steam_id=player_id)
    stats = {}

    try:
        wins = PlayerMatchSummary.objects.filter(
            player=player,
            match__validity=Match.LEGIT,
            is_win=True
        ).count()
    except IndexError:
        wins = 0
    try:
        losses = PlayerMatchSummary.objects.filter(
            player=player,
            match__validity=Match.LEGIT,
            is_win=False
        ).count()
    except IndexError:
        losses = 0
    try:
        total = PlayerMatchSummary.objects.filter(
            player=player,
        ).count()
    except IndexError:
        total = 0

    stats['wins'] = wins
    stats['losses'] = losses
    stats['total'] = total
    stats['winrate'] = round(
        float(wins) / (wins + losses) if wins + losses > 0 else 0,
        2
    )

    pms_list = get_playermatchsummaries_for_player(player, 36)
    for pms in pms_list:
        pms.display_date = \
            datetime.datetime.fromtimestamp(pms.match.start_time)\
            .strftime('%Y-%m-%d')

        pms.display_duration = \
            str(datetime.timedelta(seconds=pms.match.duration))

    datalist, params = player_winrate_json(
        player.steam_id,
        width=400,
        height=400
    )
    params['outerWidth'] = 350
    params['outerHeight'] = 350
    winrate_json = outsourceJson(datalist, params)

    #Compare to dendi and s4 by default
    player_list = [70388657, 41231571, player.steam_id]

    datalist, params = player_endgame_json(
        player_list=player_list,
        mode_list=[1, 2, 3, 4, 5],
        x_var='duration',
        y_var='K-D+.5*A',
        split_var='No Split',
        group_var='player'
    )

    params['outerWidth'] = 350
    params['outerHeight'] = 350
    endgame_json = outsourceJson(datalist, params)

    return render(
        request,
        'players/detail.html',
        {
            'player': player,
            'winrate_json': basename(winrate_json.name),
            'endgame_json': basename(endgame_json.name),
            'stats': stats,
            'pms_list': pms_list
        }
    )


@devserver_profile(follow=[CountWinrate])
def winrate(request):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero winrate for a particular player."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Modes and players you want to see here.  (Hint: don't use ability draft.)"
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
            'content': "Challenge: Who is Dendi's highest winrate hero of those with 15 games?"
        }
    ]
    tour = json.dumps(tour)
    if request.GET:
        winrate_form = PlayerWinrateLevers(request.GET)
        if winrate_form.is_valid():
            try:
                datalist, params = player_winrate_json(
                    player_id=winrate_form.cleaned_data['player'],
                    game_mode_list=winrate_form.cleaned_data['game_modes'],
                    min_date=winrate_form.cleaned_data['min_date'],
                    max_date=winrate_form.cleaned_data['max_date'],
                    role_list=winrate_form.cleaned_data['role_list'],
                    group_var=winrate_form.cleaned_data['group_var'],
                )
                json_data = outsourceJson(datalist, params)
                return render(
                    request,
                    'players/form.html',
                    {
                        'form': winrate_form,
                        'json_data': basename(json_data.name),
                        'title': 'Hero Winrate',
                        'tour': tour,
                    }
                )
            except NoDataFound:
                return render(
                    request,
                    'players/form.html',
                    {
                        'form': winrate_form,
                        'error': 'error',
                        'title': 'Hero Winrate',
                        'tour': tour,
                    }
                )
    else:
        winrate_form = PlayerWinrateLevers()

    return render(
        request,
        'players/form.html',
        {
            'form': winrate_form,
            'title': 'Hero Winrate',
            'tour': tour,
        }
    )


@devserver_profile(follow=[PlayerTimeline])
def player_hero_side(request):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero adversarial performance."
        },
    ]
    tour = json.dumps(tour)

    if request.GET:
        form = PlayerAdversarialForm(request.GET)
        if form.is_valid():
            datalist, params = player_hero_side_json(
                player_id=form.cleaned_data['player'],
                game_mode_list=form.cleaned_data['game_modes'],
                min_date=datetime.date(2009, 1, 1),
                max_date=None,
                group_var='alignment',
                plot_var=form.cleaned_data['plot_var'],
            )
            json_data = outsourceJson(datalist, params)
            return render(
                request,
                'players/form.html',
                {
                    'form': form,
                    'json_data': basename(json_data.name),
                    'title': 'Player Hero Adversary',
                    'tour': tour,
                }
            )
    else:
        form = PlayerAdversarialForm()

    return render(
        request,
        'players/form.html',
        {
            'form': form,
            'title': 'Player Hero Adversary',
            'tour': tour,
        }
    )



@devserver_profile(follow=[PlayerTimeline])
def timeline(request):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts player activity over time."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Pick a player and time bracketing to see trends in play."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For other charts, like data about heroes stats, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: About how many games has Funn1k played per week in the last month?"
        }
    ]
    tour = json.dumps(tour)

    if request.GET:
        timeline_form = PlayerTimelineForm(request.GET)
        if timeline_form.is_valid():
            image = PlayerTimeline(
                player_id=timeline_form.cleaned_data['player'],
                min_date=timeline_form.cleaned_data['min_date'],
                max_date=timeline_form.cleaned_data['max_date'],
                bucket_var=timeline_form.cleaned_data['bucket_var'],
                plot_var=timeline_form.cleaned_data['plot_var']
            )
            imagebase = basename(image.name)
            return render(
                request,
                'players/form.html',
                {
                    'form': timeline_form,
                    'image_name': imagebase,
                    'title': 'Player Timeline',
                    'tour': tour,
                }
            )
    else:
        timeline_form = PlayerTimelineForm()

    return render(
        request,
        'players/form.html',
        {
            'form': timeline_form,
            'title': 'Player Timeline',
            'tour': tour,
        }
    )


@devserver_profile(follow=[player_hero_abilities_json])
def hero_abilities(request):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts in-game level progression for two players."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare Dendi's Pudge to XBOCT's Lifestealer."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Pick two players and two heroes to compare their leveling rates."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For other charts, like data about heroes stats, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: At what level does Dendi's Pudge start falling behind Funnik's Lifestealer?"
        }
    ]
    tour = json.dumps(tour)

    if request.GET:
        form = HeroAbilitiesForm(request.GET)
        if form.is_valid():
            datalist, params = player_hero_abilities_json(
                player_1=form.cleaned_data['player_1'],
                hero_1=form.cleaned_data['hero_1'],
                player_2=form.cleaned_data['player_2'],
                hero_2=form.cleaned_data['hero_2'],
                game_modes=form.cleaned_data['game_modes'],
                division=form.cleaned_data['division'],
            )
            params['path_stroke_width'] = 1
            json_data = outsourceJson(datalist, params)
            try:
                return render(
                    request,
                    'players/form.html',
                    {
                        'form': form,
                        'json_data': basename(json_data.name),
                        'title': 'Hero Skilling Comparison',
                        'tour': tour,
                    }
                )
            except NoDataFound:
                return render(
                    request,
                    'players/form.html',
                    {
                        'form': form,
                        'error': 'error',
                        'title': 'Hero Skilling Comparison',
                        'tour': tour,
                    }
                )
    else:
        form = HeroAbilitiesForm()

    return render(
        request,
        'players/form.html',
        {
            'form': form,
            'title': 'Hero Skilling Comparison',
            'tour': tour,
        }
    )


def player_matches(request, player_id=None):
    player = get_object_or_404(Player, steam_id=player_id)
    pms_list = get_playermatchsummaries_for_player(player, 500)

    paginator = Paginator(pms_list, 36)
    page = request.GET.get('page')
    try:
        pms_list = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        pms_list = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        pms_list = paginator.page(paginator.num_pages)

    return render(
        request,
        'players/match_summary.html',
        {
            'pms_list': pms_list,
            'player': player
        }
    )


def comparison(request, player_id_1, player_id_2):
    player_1 = get_object_or_404(Player, steam_id=player_id_1)
    player_2 = get_object_or_404(Player, steam_id=player_id_2)

    datalist, params = player_versus_winrate_json(
        player_id_1=player_1.steam_id,
        player_id_2=player_2.steam_id,
        plot_var='winrate',
        )
    params['margin']['left'] = 30
    params['outerHeight'] = 300
    params['outerWidth'] = 300
    winrate_json = outsourceJson(datalist, params)

    datalist, params = player_versus_winrate_json(
        player_id_1=player_1.steam_id,
        player_id_2=player_2.steam_id,
        plot_var='usage',
        )
    params['margin']['left'] = 30
    params['outerHeight'] = 300
    params['outerWidth'] = 300
    usage_json = outsourceJson(datalist, params)

    datalist, params = player_endgame_json(
        player_list=[player_1.steam_id, player_2.steam_id],
        mode_list=[1, 2, 3, 4, 5],
        x_var='duration',
        y_var='K-D+.5*A',
        split_var='is_win',
        group_var='player',
        )
    params['outerHeight'] = 250
    params['outerWidth'] = 250
    kda_json = outsourceJson(datalist, params)

    datalist, params = player_team_endgame_json(
        player_list=[player_1.steam_id, player_2.steam_id],
        mode_list=[1, 2, 3, 4, 5],
        x_var='duration',
        y_var='K-D+.5*A',
        split_var='is_win',
        group_var='player',
        )
    params['outerHeight'] = 250
    params['outerWidth'] = 250
    team_kda_json = outsourceJson(datalist, params)

    return render(
        request,
        'players/comparison.html',
        {
            'player1': player_1,
            'player2': player_2,
            'winrate_json': basename(winrate_json.name),
            'usage_json': basename(usage_json.name),
            'kda_json': basename(kda_json.name),
            'team_kda_json': basename(team_kda_json.name),
        }
    )


def hero_style(request, player_id, hero_name):
    player = get_object_or_404(Player, steam_id=player_id)
    hero = get_object_or_404(Hero, machine_name=hero_name)

    datalist, params = hero_progression_json(
        hero=hero.steam_id,
        player=player.steam_id,
        game_mode_list=[1, 2, 3, 4, 5],
        division='Skill'
    )
    params['outerHeight'] = 275
    params['outerWidth'] = 275
    params['fadeOpacity'] = 0
    hero_progression = outsourceJson(datalist, params)

    # datalist, params = player_hero_item_json(
    #     )
    #  = outsourceJson(datalist, params)

    # datalist, params = player_hero_skill_json(
    #     )
    #  = outsourceJson(datalist, params)

    datalist, params = hero_performance_chart_json(
        hero=hero.steam_id,
        player=player.steam_id,
        game_mode_list=[1, 2, 3, 4, 5],
        x_var='duration',
        y_var='K-D+.5*A',
        group_var='skill_name',
        split_var='is_win'
    )
    params['outerHeight'] = 275
    params['outerWidth'] = 275
    params['fadeOpacity'] = 0
    hero_kda2_chart_json = outsourceJson(datalist, params)

    datalist, params = hero_performance_chart_json(
        hero=hero.steam_id,
        player=player.steam_id,
        game_mode_list=[1, 2, 3, 4, 5],
        x_var='duration',
        y_var='tower_damage',
        group_var='skill_name',
        split_var='is_win'
    )
    params['outerHeight'] = 275
    params['outerWidth'] = 275
    params['fadeOpacity'] = 0
    hero_push_json = outsourceJson(datalist, params)

    return render(
        request,
        'players/hero_style.html',
        {
            'player': player,
            'hero': hero,
            'hero_progression_json': basename(hero_progression.name),
            'hero_kda2_chart_json': basename(hero_kda2_chart_json.name),
            'hero_push_json': basename(hero_push_json.name),
        }
    )


@permission_required('players.can_touch')
def player_management(request):
    player = request_to_player(request)
    if player is not None:
        if request.method == 'POST':
            form = PlayerAddFollowForm(request.POST)
            if form.is_valid():
                follow_player_id = form.cleaned_data['player']
                follow_player = Player.objects.get(steam_id=follow_player_id)
                player.userprofile.following.add(follow_player)
        form = PlayerAddFollowForm()
        follow_list = [follow for follow in player.userprofile.following.all()]
        track_list = [track for track in player.userprofile.tracking.all()]
        return render(
            request,
            'players/management.html',
            {
                'follow_list': follow_list,
                'track_list': track_list,
                'track_limit': player.userprofile.track_limit,
                'form': form
            }
        )
    else:
        return render(
            request,
            'players/management.html',
            {
                'error': 'You need to be logged in to edit stuff here.'
            }
        )


def player_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        players = Player.objects.filter(
            persona_name__icontains=q,
            pro_name=None
        )[:20]
        pros = Player.objects.filter(
            pro_name__icontains=q
        )[:20]

        results = []
        for player in players:
            player_json = {}
            player_json['id'] = player.steam_id
            player_json['label'] = player.persona_name
            player_json['value'] = player.persona_name
            results.append(player_json)

        for player in pros:
            player_json = {}
            player_json['id'] = player.steam_id
            player_json['label'] = player.pro_name
            player_json['value'] = player.pro_name
            results.append(player_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def drop_follow(request):
    if request.is_ajax():
        drop = Player.objects.get(steam_id=request.POST['slug'])
        request.user.userprofile.following.remove(drop)
        data = request.POST['slug']
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def check_id(request):
    # @todo: The Pythonic thing, again, is to treat '' as False, and any non-
    # empty string as True.
    # --kit 2014-02-16
    if request.is_ajax() and request.POST['steam_id'] != '':
        steam_id = request.POST['steam_id']
        try:
            int(steam_id)
        except ValueError:
            data = 'We need an integer id'
            mimetype = 'application/json'
            return HttpResponseNotFound(data, mimetype)

        c = ApiContext()
        c.steamids = "{base},{check}".format(
            base=steam_id,
            check=int(steam_id) + settings.ADDER_32_BIT
        )
        vac = ValveApiCall()
        t = vac.delay(
            api_context=c,
            mode='GetPlayerSummaries'
        )
        steam_response = t.get()

        if steam_response['response']['players'] == []:
            params = {
                'player_exists': False,
                'steam_id': None,
                'name': None,
                'avatar_url': None,
                'public': False,
                'tracked': False
            }
            data = json.dumps(params)
        else:
            c = ApiContext()
            c.account_id = steam_id
            c.matches_requested = 1
            c.matches_desired = 1
            vac = ValveApiCall()
            t = vac.delay(api_context=c, mode='GetMatchHistory')
            dota_response = t.get()

            tracking = (
                len(
                    UserProfile.objects.filter(tracking__steam_id=steam_id)
                ) != 0
                or len(
                    Player.objects.filter(steam_id=steam_id, updated=True)
                ) != 0
            )
            if dota_response['result']['status'] != 1:
                params = {
                    'player_exists': True,
                    'steam_id': steam_response[
                        'response'
                    ]['players'][0]['steamid'],
                    'name': steam_response[
                        'response'
                    ]['players'][0]['personaname'].encode('utf-8'),
                    'avatar_url': steam_response[
                        'response'
                    ]['players'][0]['avatarmedium'],
                    'public': False,
                    'tracked': tracking
                }
                data = json.dumps(params)
            else:
                params = {
                    'player_exists': True,
                    'steam_id': steam_response[
                        'response'
                    ]['players'][0]['steamid'],
                    'name': steam_response[
                        'response'
                    ]['players'][0]['personaname'].encode('utf-8'),
                    'avatar_url': steam_response[
                        'response'
                    ]['players'][0]['avatarmedium'],
                    'public': True,
                    'tracked': tracking
                }
                data = json.dumps(params)
        if (
                params['player_exists']
                and params['public']
                and not params['tracked']
                ):
        # @todo: This crap should be in templates. If you are writing HTML in
        # a string in a Python file, check yourself.
        # --kit 2014-02-16
            data = """<tr>
              <td>{exists}</td>
              <td>{id}</td>
              <td>{name}</td>
              <td><img src='{image}'></td>
              <td>{public}</td>
              <td>{tracked}</td>
              <td><input type="button" id="add_track" name="{id}" value="Import!" /></td>
              </tr>""".format(
                exists=params['player_exists'],
                id=params['steam_id'],
                name=params['name'],
                public=params['public'],
                image=params['avatar_url'],
                tracked=params['tracked'],
                )
        else:
            data = """<tr>
              <td>{exists}</td>
              <td>{id}</td>
              <td>{name}</td>
              <td><img src='{image}'></td>
              <td>{public}</td>
              <td>{tracked}</td>
              <td>Not available</td>
              </tr>""".format(
                exists=params['player_exists'],
                id=params['steam_id'],
                name=params['name'],
                public=params['public'],
                image=params['avatar_url'],
                tracked=params['tracked'],
                )

    else:
        data = 'fail'
        mimetype = 'application/json'
        return HttpResponseNotFound(data, mimetype)
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def add_track(request):
    if request.is_ajax():
        steam_id = int(request.POST['steam_id']) % settings.ADDER_32_BIT
        try:
            track = Player.objects.get(steam_id=steam_id)
        except Player.DoesNotExist:
            track = Player.objects.create(steam_id=steam_id)

        if request.user.userprofile.tracking.add(track):
            data = request.POST['steam_id']

            # Refresh all the names
            c = ApiContext()
            vac = ValveApiCall()
            upp = UpdatePlayerPersonas()
            c.steamids = steam_id + settings.ADDER_32_BIT
            chain(vac.s(
                mode='GetPlayerSummaries',
                api_context=c
            ), upp.s()).delay()

            # Pull in the new guy.
            apd = AcquirePlayerData()
            c = ApiContext()
            c.account_id = steam_id
            apd.delay(api_context=c)

        else:
            data = 'fail'
        mimetype = 'application/json'
        return HttpResponse(data, mimetype)

    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


def get_playermatchsummaries_for_player(player, count):
    pms_list = PlayerMatchSummary.objects.select_related()
    pms_list = pms_list.filter(
        player=player
    ).order_by('-match__start_time')[0:count]
    for pms in pms_list:
        pms.display_date = datetime.datetime.fromtimestamp(
            pms.match.start_time
        ).strftime('%Y-%m-%d')
        pms.display_duration = str(datetime.timedelta(
            seconds=pms.match.duration
        ))
        pms.KDA2 = pms.kills - pms.deaths + pms.assists / 2.0
        # @todo: Again, postposed conditionals.
        # --kit 2014-02-16
        pms.color_class = 'pos' if pms.KDA2 > 0 else 'neg'
        pms.mag = abs(pms.KDA2)*2
    return pms_list
