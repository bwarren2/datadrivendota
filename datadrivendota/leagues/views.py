from django.views.generic import ListView, DetailView
from utils.pagination import SmarterPaginator

from .models import League
from matches.models import Match, PlayerMatchSummary
from matches.views import annotated_matches


class LeagueList(ListView):
    """The index of imported leagues"""
    model = League

    def get_queryset(self):
        qs = self.model.recency.all().select_related()
        return qs


class LeagueDetail(DetailView):
    """Focusing on a particular league"""

    def get_object(self):
        return League.objects.get(steam_id=self.kwargs.get('steam_id'))

    def get_context_data(self, **kwargs):
        print self.object.steam_id
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
