import json

from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required
from django.conf import settings

from players.models import Player
from accounts.models import UserProfile
from players.forms import PlayerAddFollowForm
from datadrivendota.forms import ApplicantForm
from heroes.models import Hero
from matches.models import Match

from accounts.models import MatchRequest
from datadrivendota.forms import MatchRequestForm
from matches.management.tasks.valve_api_calls import AcquireMatches

from .models import request_to_player, Applicant
from .forms import PollForm

from datadrivendota.views import LoginRequiredView
from utils.exceptions import DataCapReached, ValidationException


from celery import chain
from django.conf import settings
from django.http import HttpResponse, HttpResponseNotFound


from matches.management.tasks.valve_api_calls import (
    ApiContext,
    ValveApiCall,
    UpdatePlayerPersonas,
    AcquirePlayerData,
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
            'accounts/management.html',
            {
                'follow_list': follow_list,
                'track_list': track_list,
                'track_limit': player.userprofile.track_limit,
                'form': form
            }
        )


class TrackingView(LoginRequiredView, TemplateView):
    """Where users can adjust who they follow"""
    template_name = 'accounts/tracking.html'

    def get_context_data(self, *args, **kwargs):
        if 'follow_list' not in kwargs:
            kwargs['track_list'] = [
                track for track in self.request.user.userprofile.tracking.all()
            ]
        return super(TrackingView, self).get_context_data(*args, **kwargs)


class FollowView(LoginRequiredView, FormView):
    """Where users can adjust who they follow"""
    form_class = PlayerAddFollowForm
    template_name = 'accounts/follow.html'

    def form_valid(self, form):
        follow_player_id = form.cleaned_data['player']
        follow_player = Player.objects.get(steam_id=follow_player_id)
        self.request.user.userprofile.following.add(follow_player)
        messages.add_message(self.request, messages.SUCCESS, "Follow added")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, *args, **kwargs):
        if 'follow_list' not in kwargs:
            kwargs['follow_list'] = [
                follow for follow in
                self.request.user.userprofile.following.all()
            ]
        return super(FollowView, self).get_context_data(*args, **kwargs)


class MatchRequestView(LoginRequiredView, FormView):
    form_class = MatchRequestForm
    template_name = 'accounts/match_import_request.html'
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


class PollView(FormView):
    """Where users can adjust who they follow"""
    form_class = PollForm
    template_name = 'accounts/poll.html'

    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Follow added")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        context = super(PollView, self).get_context_data(**kwargs)
        hero_id_names = {
            hero.steam_id: hero.internal_name
            for hero in Hero.public.all()
        }
        m = Match.objects.get(steam_id=787453665)
        context['match_replay_url'] = 'http://127.0.0.1:8000'+m.replay.url
        print context['match_replay_url']
        context['hero_json'] = json.dumps(hero_id_names)
        return context


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
    if request.is_ajax() and request.POST['steam_id']:
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
            data = json.dumps({
                'exists': params['player_exists'],
                'id': params['steam_id'],
                'name': params['name'],
                'public': params['public'],
                'image': params['avatar_url'],
                'tracked': params['tracked'],
                'cleared': True,
            })
        else:
            data = json.dumps({
                'exists': params['player_exists'],
                'id': params['steam_id'],
                'name': params['name'],
                'public': params['public'],
                'image': params['avatar_url'],
                'tracked': params['tracked'],
                'cleared': False,
            })

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

        if request.user.userprofile.add_tracking(track):
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
