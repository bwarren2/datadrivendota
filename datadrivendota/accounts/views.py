import json
from os import getenv

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
from matches.management.tasks import MirrorMatches

from .models import request_to_player, Applicant, PollResponse
from .forms import PollForm

from datadrivendota.views import LoginRequiredView
from utils.exceptions import DataCapReached, ValidationException


from celery import chain
from django.http import HttpResponse, HttpResponseNotFound


from datadrivendota.management.tasks import (
    ApiContext,
    ValveApiCall,
)
from players.management.tasks import MirrorClientPersonas
from players.management.tasks import MirrorPlayerData


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
            task = MirrorMatches()
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
    form_class = PollForm
    template_name = 'accounts/poll.html'

    def form_valid(self, form):
        messages.add_message(
            self.request,
            messages.SUCCESS,
            "Answer Submitted!"
        )

        if form.cleaned_data['premium'] == 'yes':
            premium = True
        else:
            premium = False

        PollResponse.objects.create(
            steam_id=int(form.cleaned_data['steam_id']),
            interested_in_premium=premium
        )
        return self.response_class(
            request=self.request,
            template='poll_response.html',
            context=self.get_context_data(form=form),
        )

    def get_context_data(self, **kwargs):
        context = super(PollView, self).get_context_data(**kwargs)
        hero_id_names = {
            hero.steam_id: hero.internal_name
            for hero in Hero.public.all()
        }
        m = Match.objects.get(steam_id=787453665)

        # Local storages use relative urls, prod uses absolute.  Annoying.
        if getenv('DJANGO_SETTINGS_MODULE') == 'datadrivendota.settings.local':
            context['match_replay_url'] = 'http://127.0.0.1:8000'+m.replay.url
        else:
            context['match_replay_url'] = m.replay.url

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
            upp = MirrorClientPersonas()
            c.steamids = steam_id + settings.ADDER_32_BIT
            chain(vac.s(
                mode='GetPlayerSummaries',
                api_context=c
            ), upp.s()).delay()

            # Pull in the new guy.
            apd = MirrorPlayerData()
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
