from django.views.generic.edit import FormView
from django.views.generic.base import TemplateView
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import permission_required

from players.models import Player
from accounts.models import UserProfile
from players.forms import PlayerAddFollowForm
from datadrivendota.forms import ApplicantForm

from accounts.models import MatchRequest
from datadrivendota.forms import MatchRequestForm
from matches.management.tasks.valve_api_calls import AcquireMatches

from .models import request_to_player, Applicant

from datadrivendota.views import LoginRequiredView
from utils.exceptions import DataCapReached, ValidationException


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
            'data_management/management.html',
            {
                'follow_list': follow_list,
                'track_list': track_list,
                'track_limit': player.userprofile.track_limit,
                'form': form
            }
        )


class TrackingView(LoginRequiredView, TemplateView):
    """Where users can adjust who they follow"""
    template_name = 'data_management/tracking.html'

    def get_context_data(self, *args, **kwargs):
        if 'follow_list' not in kwargs:
            kwargs['track_list'] = [
            track for track in self.request.user.userprofile.tracking.all()
        ]
        return super(TrackingView, self).get_context_data(*args, **kwargs)


class FollowView(LoginRequiredView, FormView):
    """Where users can adjust who they follow"""
    form_class = PlayerAddFollowForm
    template_name = 'data_management/follow.html'

    def form_valid(self, form):
        follow_player_id = form.cleaned_data['player']
        follow_player = Player.objects.get(steam_id=follow_player_id)
        self.request.user.userprofile.following.add(follow_player)
        messages.add_message(self.request, messages.SUCCESS, "Follow added")
        return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, *args, **kwargs):
        if 'follow_list' not in kwargs:
            kwargs['follow_list'] = [
            follow for follow in self.request.user.userprofile.following.all()
        ]
        return super(FollowView, self).get_context_data(*args, **kwargs)


class MatchRequestView(LoginRequiredView, FormView):
    form_class = MatchRequestForm
    template_name = 'data_management/match_import_request.html'
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
