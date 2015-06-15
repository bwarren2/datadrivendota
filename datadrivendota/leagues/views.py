from rest_framework import viewsets, filters
from django.views.generic import ListView, DetailView, TemplateView
from utils.pagination import SmarterPaginator

from .models import League, ScheduledMatch
from .serializers import LeagueSerializer
from matches.models import Match
from datadrivendota.redis_app import (
    get_games,
)


class ScheduledMatchList(ListView):

    """ The index of imported leagues. """

    model = ScheduledMatch
    paginate_by = 32

    def paginate_queryset(self, queryset, page_size):
        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=queryset,
            per_page=page_size,
            current_page=page
        )
        objs = paginator.current_page
        return (paginator, page, objs, True)


class LeagueList(ListView):

    """ The index of imported leagues. """

    model = League
    paginate_by = 32

    def get_queryset(self):
        qs = self.model.recency.all().select_related()
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


class LeagueDetail(DetailView):

    """ Focusing on a particular league. """

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
            per_page=2,
            current_page=page
        )
        match_list = paginator.current_page

        context = {
            'match_list': match_list,
        }
        return super(LeagueDetail, self).get_context_data(**context)


class LiveGameListView(TemplateView):
    title = "Particular Game!"
    template_name = "leagues/live_game_list.html"

    def get_context_data(self, **kwargs):

        context = {
            'games': sorted(
                get_games(),
                key=get_duration,
                reverse=True
            )
        }
        return super(LiveGameListView, self).get_context_data(**context)


class LiveGameDetailView(TemplateView):

    """ Watch a live game. Lots of template magic. """

    title = "Live Games!"
    template_name = "leagues/live_game_detail.html"

    def get_context_data(self, **kwargs):

        match_id = int(kwargs['match_id'])
        context = {
            'match_id': match_id
        }
        return super(LiveGameDetailView, self).get_context_data(**context)


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    paginate_by = 10


def get_duration(game):
    """ Helper function for sorting."""
    return game['scoreboard']['duration'] if 'scoreboard' in game else 0
