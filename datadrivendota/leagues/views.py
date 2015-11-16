from time import time
from django.views.generic import ListView, DetailView, TemplateView
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.conf import settings
from django.db.models import Max, Count

from utils.pagination import SmarterPaginator
from datadrivendota.views import JsonApiView

from .models import League, ScheduledMatch, LiveMatch
from matches.models import Match

from datadrivendota.redis_app import (
    get_games,
    timeline_key,
    redis_app,
    slice_key
)


class LeagueOverview(TemplateView):

    """ The leagues with recent games by category. """

    template_name = 'leagues/league_overview.html'
    item_count = 3

    def get_context_data(self, **kwargs):
        kwargs['premium_list'] = League.recency.filter(
            tier=League.PREMIUM
        ).select_related()[:self.item_count]
        kwargs['pro_list'] = League.recency.filter(
            tier=League.PRO
        ).select_related()[:self.item_count]
        kwargs['am_list'] = League.recency.filter(
            tier=League.AMATEUR
        ).select_related()[:self.item_count]
        return super(LeagueOverview, self).get_context_data(**kwargs)


class LeagueList(ListView):

    """ The index of imported leagues. """

    model = League
    paginate_by = 32

    def get_queryset(self, **kwargs):
        if self.kwargs['tier'] == League.URL_MAP[League.PREMIUM]:
            qs = self.model.recency.filter(
                tier=League.PREMIUM
            ).select_related()
        elif self.kwargs['tier'] == League.URL_MAP[League.PRO]:
            qs = self.model.recency.filter(tier=League.PRO).select_related()
        elif self.kwargs['tier'] == League.URL_MAP[League.AMATEUR]:
            qs = self.model.recency.filter(
                tier=League.AMATEUR
            ).select_related()
        else:
            raise Http404
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

    def get_context_data(self, **kwargs):
        kwargs['tier'] = "{0} Leagues".format(self.kwargs['tier'].title())
        return super(LeagueList, self).get_context_data(**kwargs)


class LeagueDetail(DetailView):

    """ Focusing on a particular league. """

    def get_object(self):
        return get_object_or_404(League.recency, steam_id=self.kwargs.get('steam_id'))

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

        validity_metrics = Match.objects.filter(league__steam_id=2733)\
            .values('validity')\
            .annotate(total=Count('validity'))\
            .order_by()


        for itm in validity_metrics:
            itm['name'] = dict(Match.VALIDITY_CHOICES)[itm['validity']]

        try:
            max_match_time = League.objects.filter(
                steam_id=self.kwargs.get('steam_id')
            ).annotate(Max('match__start_time'))[0].match__start_time__max
        except League.DoesNotExist:
            max_match_time = time()

        kwargs['validity_metrics'] = validity_metrics
        kwargs['max_match_time'] = max_match_time
        kwargs['match_list'] = match_list
        kwargs['show_date_control_bar'] = True
        return super(LeagueDetail, self).get_context_data(**kwargs)


class LeagueDetailTimeWalk(DetailView):

    """ Timestepping for a particular league. """

    template_name = 'leagues/league_timewalk.html'

    def get_object(self):
        return get_object_or_404(League, steam_id=self.kwargs.get('steam_id'))

    def get_context_data(self, **kwargs):
        kwargs['show_control_bar'] = True
        return super(LeagueDetailTimeWalk, self).get_context_data(**kwargs)


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


class LiveMatchList(ListView):

    """ The index of imported leagues. """

    model = LiveMatch

    def get_context_data(self, **kwargs):
        """
        Created lists of matches flagging if we have pulled in their data.

        This logic will probably be factored out into managers or something.
        """
        live_matches = LiveMatch.objects.all()

        matches = Match.objects.filter(
            steam_id__in=[x.steam_id for x in live_matches]
        ).values_list('steam_id', flat=True)

        for match in live_matches:

            if match.steam_id in matches:
                match.has_match = True
            else:
                match.has_match = False

            if match.has_match:
                match.finished = True
            elif match.ready is False:
                match.finished = 'Unready'
            else:
                match.finished = False

        kwargs['complete_matches'] = [
            x for x in live_matches if x.has_match
        ]
        kwargs['incomplete_matches'] = [
            x for x in live_matches
            if x.finished is False and x.ready and not x.failed
        ]
        kwargs['unready_matches'] = [
            x for x in live_matches if x.ready is False
        ]
        kwargs['failed_matches'] = [
            x for x in live_matches if x.failed and not x.has_match
        ]

        return super(LiveMatchList, self).get_context_data(**kwargs)


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


class ApiLiveGamesList(JsonApiView):

    def fetch_json(self, *args, **kwargs):
        data = get_games()
        return data


class ApiLiveGameDetail(JsonApiView):

    def get_context_data(self, **kwargs):
        if 'match_id' in kwargs:
            kwargs['match_id'] = int(kwargs['match_id'])
        return kwargs

    def fetch_json(self, *args, **kwargs):
        key = timeline_key(kwargs['match_id'])
        data = redis_app.get(key)
        if data is not None:
            return data
        else:
            self.fail()


class ApiLiveGameSlice(JsonApiView):

    def get_context_data(self, **kwargs):
        if 'match_id' in kwargs:
            kwargs['match_id'] = int(kwargs['match_id'])
        return kwargs

    def fetch_json(self, *args, **kwargs):
        key = slice_key(kwargs['match_id'])
        data = redis_app.get(key)
        if data is not None:
            return data
        else:
            self.fail()


def get_duration(game):
    """ Helper function for sorting."""
    return game['scoreboard']['duration'] if 'scoreboard' in game else 0
