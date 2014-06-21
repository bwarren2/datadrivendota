import json

from django.http import HttpResponse
from django.views.generic import ListView, DetailView
from django.db.models import Q
from utils.pagination import SmarterPaginator

from .models import Team
from matches.models import Match, PlayerMatchSummary
from matches.views import annotated_matches
from .mixins import (
    WinrateMixin,
    PickBanMixin,
)
from datadrivendota.views import ChartFormView, ApiView


class TeamList(ListView):
    """The index of imported leagues"""
    model = Team
    paginate_by = 30
    template_name = 'teams/team_list.html'

    def get_queryset(self):
        qs = self.model.sorted.all()
        return qs

    def paginate_queryset(self, queryset, page_size):
        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=queryset,
            per_page=page_size,
            current_page=page
        )
        objs = paginator.current_page
        return (paginator, page, objs, True)


class TeamDetail(DetailView):
    """Focusing on a particular team"""

    def get_object(self):
        return Team.objects.get(steam_id=self.kwargs.get('steam_id'))

    def get_context_data(self, **kwargs):
        print self.object.steam_id
        match_list = Match.objects.filter(
            skill=4
            )
        match_list = match_list.filter(
            Q(radiant_team__steam_id=self.object.steam_id) |
            Q(dire_team__steam_id=self.object.steam_id)
            )

        match_list = match_list.select_related()\
            .distinct().order_by('-start_time')

        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=match_list,
            per_page=15,
            current_page=page
        )
        match_list = paginator.current_page

        pms_list = PlayerMatchSummary.\
            objects.filter(match__in=match_list)\
            .select_related().order_by('-match__start_time')[:500]
        match_data = annotated_matches(pms_list, [])

        context = {
            'match_list': match_list,
            'match_data': match_data,
        }
        return super(TeamDetail, self).get_context_data(**context)


class Winrate(WinrateMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero winrate for a particular team."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Dates and the team you want to see here."
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Try it out!"
        }
    ]
    title = "Hero Winrate"
    html = "players/form.html"


class PickBan(PickBanMixin, ChartFormView):
    """What did this team pick/ban?"""
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts picks and bans for matches that have a given team.  (Both side's picks and bans count.)"
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Dates and the team you want to see here."
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Try it out!?"
        }
    ]
    title = "Pick/Bans"
    html = "players/form.html"


class ApiWinrateChart(WinrateMixin, ApiView):
    pass


class ApiPickBanChart(PickBanMixin, ApiView):
    pass


def team_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        teams = Team.objects.filter(
            teamdossier__name__icontains=q,
        )[:20]
        print q, teams
        results = []
        for team in teams:
            team_json = {}
            team_json['id'] = team.steam_id
            team_json['label'] = team.teamdossier.name
            team_json['value'] = team.teamdossier.name
            results.append(team_json)

        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
