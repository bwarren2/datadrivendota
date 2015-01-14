import json
from django.http import HttpResponse

from django.views.generic import ListView, DetailView
from utils.pagination import SmarterPaginator

from .models import League
from matches.models import Match, PlayerMatchSummary
from matches.views import annotated_matches
from .mixins import (
    WinrateMixin,
    PickBanMixin,
)
from datadrivendota.views import ChartFormView, ApiView


class LeagueList(ListView):
    """The index of imported leagues"""
    model = League
    paginate_by = 32

    def get_queryset(self):
        qs = self.model.recency.all().select_related().exclude(
            leaguedossier__logo_image=None
            )
        return qs

    def paginate_queryset(self, queryset, page_size):
        page = self.request.GET.get('page')
        print "QSs:"
        for x in queryset:
            print x.leaguedossier.name
        paginator = SmarterPaginator(
            object_list=queryset,
            per_page=page_size,
            current_page=page
        )
        objs = paginator.current_page
        print "Objs:"
        for x in objs:
            print x.leaguedossier.name
        print page_size, len(objs)
        return (paginator, page, objs, True)


class LeagueDetail(DetailView):
    """Focusing on a particular league"""

    def get_object(self):
        return League.objects.get(steam_id=self.kwargs.get('steam_id'))

    def get_context_data(self, **kwargs):
        match_list = Match.objects.filter(
            league=self.object
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
        return super(LeagueDetail, self).get_context_data(**context)


class Winrate(WinrateMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero winrate for a particular league."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Dates and the league you want to see here."
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
    """What did this league pick/ban?"""
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts picks and bans for matches that have a given league.  (Both side's picks and bans count.)"
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Dates and the league you want to see here."
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


def league_list(request):
    if request.is_ajax():
        q = request.GET.get('term', '')
        leagues = League.objects.filter(
            leaguedossier__name__icontains=q,
        )[:20]
        results = []
        for league in leagues:
            league_json = {}
            league_json['id'] = league.steam_id
            league_json['label'] = league.leaguedossier.display_name
            league_json['value'] = league.steam_id
            results.append(league_json)

        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)
