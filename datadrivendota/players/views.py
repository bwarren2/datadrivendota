"""Views primarily related to players, as a group or particularly."""
from json import dumps
from django.http import HttpResponse, Http404
from django.db.models import Max
from django.views.generic import ListView, DetailView, TemplateView, View
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from accounts.models import (
    get_relevant_player_ids,
)
from .models import Player
from .management.tasks import MirrorPlayerData
from datadrivendota.management.tasks import ApiContext

import logging
logger = logging.getLogger(__name__)


class PlayerIndexView(ListView):

    """A list of active or paid users."""

    paginate_by = 30

    def get_queryset(self):
        return Player.objects.filter(
            steam_id__in=get_relevant_player_ids()
        ).annotate(
            Max('playermatchsummary__match__start_time')
        ).order_by(
            '-playermatchsummary__match__start_time__max'
        )


class ProIndexView(ListView):

    """List the players that have pro names."""

    paginate_by = 30

    def get_queryset(self):
        """ Get the list of players to display."""
        return Player.objects.exclude(pro_name=None)


class PlayerDetailView(DetailView):

    """ Get a closer look at a particular player."""

    def get_object(self):
        return get_object_or_404(Player, steam_id=self.kwargs.get('player_id'))

    def get_context_data(self, **kwargs):

        kwargs['player'] = self.object
        kwargs['pms_list'] = self.object.summaries(36)
        return super(PlayerDetailView, self).get_context_data(**kwargs)

    def get_winrate(self, stats):
        """ Calculate a winrate, allowing for the option of no games played."""
        if stats['total'] > 0:
            return round(float(stats['wins']) / stats['total'] * 100)
        else:
            return 0


class DashView(TemplateView):
    template_name = 'players/dash.html'

    @method_decorator(staff_member_required)
    def dispatch(self, *args, **kwargs):
        return super(DashView, self).dispatch(*args, **kwargs)


class TasksView(View):

    def post(self, request, *args, **kwargs):
        if request.is_ajax() and request.user.is_staff:

            response_data = {}

            player_id = request.POST['player_id']
            match_ct = request.POST['match_ct']
            task = request.POST['task']
            if task == 'create':
                t = MirrorPlayerData()
                c = ApiContext()
                c.matches_requested = match_ct
                c.matches_desired = match_ct
                c.account_id = player_id
                t.delay(api_context=c)

                response_data['result'] = "Getting {0} matches for {1}".format(
                    match_ct, player_id
                )
                response_data['type'] = 'success'

            return HttpResponse(
                dumps(response_data),
                content_type="application/json"
            )
        else:
            raise Http404
