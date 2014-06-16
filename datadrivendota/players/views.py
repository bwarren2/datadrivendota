import datetime
import json
from time import mktime
from random import choice
from celery import chain
from django.conf import settings
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from .models import Player, UserProfile
from .forms import (
    PlayerAddFollowForm,
    ApplicantForm,
    PlayerMatchesFilterForm
)

from utils.pagination import SmarterPaginator

from players.models import MatchRequest
from datadrivendota.forms import MatchRequestForm
from matches.models import PlayerMatchSummary, Match
from matches.management.tasks.valve_api_calls import (
    ApiContext,
    ValveApiCall,
    UpdatePlayerPersonas,
    AcquirePlayerData,
    AcquireMatches
)
from .models import request_to_player, Applicant

from .mixins import (
    WinrateMixin,
    HeroAdversaryMixin,
    HeroAbilitiesMixin,
    VersusWinrateMixin,
    RoleMixin,
    )

from heroes.models import Hero
from datadrivendota.views import ChartFormView, ApiView, LoginRequiredView
from utils.exceptions import DataCapReached, ValidationException

if settings.VERBOSE_PROFILING:
    try:
        from line_profiler import LineProfiler

        def do_profile(follow=[]):
            def inner(func):
                def profiled_func(*args, **kwargs):
                    try:
                        profiler = LineProfiler()
                        profiler.add_function(func)
                        for f in follow:
                            profiler.add_function(f)
                        profiler.enable_by_count()
                        return func(*args, **kwargs)
                    finally:
                        profiler.print_stats()
                return profiled_func
            return inner

    except ImportError:
        def do_profile(follow=[]):
            "Helpful if you accidentally leave in production!"
            def inner(func):
                def nothing(*args, **kwargs):
                    return func(*args, **kwargs)
                return nothing
            return inner
else:
    def do_profile(follow=[]):
        "Helpful if you accidentally leave in production!"
        def inner(func):
            def nothing(*args, **kwargs):
                return func(*args, **kwargs)
            return nothing
        return inner


def index(request):
    player_list = Player.objects.filter(updated=True)
    return render(
        request,
        'players/index.html',
        {
            'player_list': player_list
        }
    )


def data_applicant(request):
    if request.method == 'POST':
        form = ApplicantForm(request.POST)
        if form.is_valid():

            """This is some stupid hacky stuff.  What we really want to do is have a uniqueness criterion on the model, a 32bit validator on the field, and a clean() method on the field that takes % 32bit.  We'll do it later."""
            try:
                modulo_id = form.cleaned_data['steam_id'] \
                    % settings.ADDER_32_BIT
                test = Applicant.objects.get(
                    steam_id=modulo_id
                )
                status = 'preexisting'
            except Applicant.DoesNotExist:
                form.save()
                status = 'success'

            return render(
                request,
                'players/data_applicant.html',
                {
                    'form': form,
                    status: status
                }
            )
        else:
            status = 'error'
            return render(
                request,
                'players/data_applicant.html',
                {
                    'form': form,
                    status: status
                }
            )
    else:
        form = ApplicantForm()
        return render(
            request,
            'players/data_applicant.html',
            {'form': form}
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

@do_profile()
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

    if request.user.is_authenticated():
        compare_url = reverse(
            'players:comparison',
            kwargs={
                'player_id_1': request.user.userprofile.player.steam_id,
                'player_id_2': player.steam_id,
            })
        compare_str = 'Compare me to {p2}!'.format(p2=player.display_name)
    else:
        p2 = Player.objects.exclude(
            pro_name=None,
        ).exclude(
            steam_id=player.steam_id,
        ).filter(
            updated=True,
        )
        p2 = choice([p for p in p2])
        compare_url = reverse(
            'players:comparison',
            kwargs={
                'player_id_1': player.steam_id,
                'player_id_2': p2.steam_id,
            })
        compare_str = 'Compare {p1} to {p2}!'.format(
            p1=player.display_name,
            p2=p2.display_name,
        )

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

    #Compare to dendi and s4 by default
    player_list = [70388657, 41231571, player.steam_id]
    endgame_players = Player.objects.filter(steam_id__in=player_list)
    player_names = ",".join([p.persona_name for p in endgame_players])

    return render(
        request,
        'players/detail.html',
        {
            'player': player,
            'endgame_chart_names': player_names,
            'stats': stats,
            'compare_url': compare_url,
            'compare_str': compare_str,
            'pms_list': pms_list
        }
    )


class Winrate(WinrateMixin, ChartFormView):
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
    title = "Hero Winrate"
    html = "players/form.html"


class HeroAdversary(HeroAdversaryMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero adversarial performance."
        },
    ]
    title = "Player Hero Adversary"
    html = "players/form.html"


class HeroAbilities(HeroAbilitiesMixin, ChartFormView):
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
    title = "Hero Skilling Comparison"
    html = "players/form.html"

    def amend_params(self, chart):
        chart.params.path_stroke_width = 1
        return chart


def player_matches(request, player_id=None):
    player = get_object_or_404(Player, steam_id=player_id)
    total_results = 500
    if request.method == 'POST':
        form = PlayerMatchesFilterForm(request.POST)
        if form.is_valid():
            print form.cleaned_data
            pms_list = PlayerMatchSummary.objects.select_related()
            pms_list = pms_list.filter(
                player=player
            )
            if form.cleaned_data['hero'] is not None:
                pms_list = pms_list.filter(
                    hero__steam_id=form.cleaned_data['hero']
                )
            if form.cleaned_data['min_date'] is not None:
                min_date_utc = mktime(
                    form.cleaned_data['min_date'].timetuple()
                    )
                pms_list = pms_list.filter(
                    match__start_time__gte=min_date_utc,
                )
            if form.cleaned_data['max_date'] is not None:
                max_date_utc = mktime(
                    form.cleaned_data['max_date'].timetuple()
                    )
                pms_list = pms_list.filter(
                    match__start_time__lte=max_date_utc,
                )
            pms_list = pms_list.order_by('-match__start_time')[0:total_results]
            pms_list = date_notate_pms_list(pms_list)
        else:
            pms_list = get_playermatchsummaries_for_player(
                player, total_results
            )
    else:
        form = PlayerMatchesFilterForm()
        pms_list = get_playermatchsummaries_for_player(player, total_results)

    page = request.GET.get('page')
    paginator = SmarterPaginator(
        object_list=pms_list,
        per_page=36,
        current_page=page
    )
    pms_list = paginator.current_page

    return render(
        request,
        'players/match_summary.html',
        {
            'pms_list': pms_list,
            'player': player,
            'form': form
        }
    )


def comparison(request, player_id_1, player_id_2):
    player_1 = get_object_or_404(Player, steam_id=player_id_1)
    player_2 = get_object_or_404(Player, steam_id=player_id_2)

    return render(
        request,
        'players/comparison.html',
        {
            'player1': player_1,
            'player2': player_2,
        }
    )


def hero_style(request, player_id, hero_name):
    #So much magic in the template!
    player = get_object_or_404(Player, steam_id=player_id)
    hero = get_object_or_404(Hero, machine_name=hero_name)

    return render(
        request,
        'players/hero_style.html',
        {
            'player': player,
            'hero': hero,
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


class MatchRequestView(FormView):
    form_class = MatchRequestForm
    template_name = 'players/match_import_request.html'
    initial = {}

    def form_invalid(self, form):
        super(MatchRequestView, self).form_invalid(form)

    def form_valid(self, form):

        match_id = form.cleaned_data['match_id']
        try:
            match_request = MatchRequest.create_for_user(
                self.request.user, match_id
            )

            msg = "Request submitted!  We have tossed this in the task queue.  It should be finished in the next two minutes, and then <a href='{0}'>this link</a> will work".format(
                reverse(
                    'matches:match_detail',
                    kwargs={'match_id': match_request.match_id}
                ))
            task = AcquireMatches()
            task.delay(matches=[match_request.match_id])
            messages.add_message(self.request, messages.SUCCESS, msg)

        except ValidationException as err:
            msg = err.strerror
            messages.add_message(self.request, messages.WARNING, msg)
        except DataCapReached:
            msg = ("You have reached your import cap.",
                   "  We are working at increasing this.")
            messages.add_message(self.request, messages.WARNING, msg)
        return render(
            self.request,
            self.template_name,
            {
                'form': form
            }
        )

    def get_success_url(self):
        return reverse('players:management')


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
    pms_list = date_notate_pms_list(pms_list)
    return pms_list


def date_notate_pms_list(pms_list):
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
        if pms.KDA2 > 0:
            pms.color_class = 'pos'
            pms.pos = True
        else:
            pms.color_class = 'neg'
            pms.neg = True

        pms.mag = abs(pms.KDA2)*3

        if pms.match.validity == Match.LEGIT:
            pms.legit = True
        elif pms.match.validity == Match.UNCOUNTED:
            pms.invalid = True
        elif pms.match.validity == Match.UNPROCESSED:
            pms.unprocessed = True

    return pms_list


class ApiWinrateChart(WinrateMixin, ApiView):
    pass


class ApiHeroAdversary(HeroAdversaryMixin, ApiView):
    pass


class ApiHeroAbilities(HeroAbilitiesMixin, ApiView):
    pass


class ApiVersusWinrate(VersusWinrateMixin, ApiView):
    pass


class ApiRole(RoleMixin, ApiView):
    pass
