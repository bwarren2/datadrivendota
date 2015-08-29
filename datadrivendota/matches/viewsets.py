from rest_framework import viewsets, filters

from .models import Match, PlayerMatchSummary, PickBan, SkillBuild, GameMode

from .serializers import (
    MatchSerializer,
    PlayerMatchSummarySerializer,
    SkillBuildSerializer,
    FastMatchPickBansSerializer,
    PickbanSerializer,
)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 400

    def get_queryset(self):
        queryset = Match.objects.all()\
            .prefetch_related('radiant_team')\
            .prefetch_related('dire_team')\
            .given(self.request)\
            .order_by('start_time')

        limit = self.request.query_params.get(self.page_size_query_param)

        if limit is not None:
            result_limit = min(limit, self.max_page_size)
            queryset = queryset[:result_limit]
        else:
            queryset = queryset[:self.page_size]

        return queryset.select_related()


import time
from rest_framework.response import Response

from django.core.signals import request_started, request_finished
global serializer_time
global db_time
global filter_time
global dispatch_time
global render_time


class MatchPickBanViewSet(viewsets.ReadOnlyModelViewSet):
    page_size = 10
    page_size_query_param = 'page_size'
    serializer_class = FastMatchPickBansSerializer
    max_page_size = 200

    def list(self, request, *args, **kwargs):
        global serializer_time
        global db_time
        global filter_time

        db_start = time.time()
        qs = self.get_queryset()
        qs = list(qs)
        db_end = time.time()
        db_time = db_end - db_start

        self.object_list = self.filter_queryset(qs)
        filter_time = time.time() - db_end

        # Switch between paginated or standard style responses
        page = self.paginate_queryset(self.object_list)
        if page is not None:
            serializer = self.get_pagination_serializer(page)
        else:
            serializer = self.get_serializer(self.object_list, many=True)
        serializer_start = time.time()
        data = serializer.data
        serializer_time = time.time() - serializer_start
        return Response(data)

    def dispatch(self, request, *args, **kwargs):
        global dispatch_time
        global render_time

        dispatch_start = time.time()
        ret = super(MatchPickBanViewSet, self).dispatch(
            request, *args, **kwargs
        )

        render_start = time.time()
        ret.render()
        render_time = time.time() - render_start

        dispatch_time = time.time() - dispatch_start

        return ret

    def _get_matches(self):
        matches = Match.objects.filter(
            game_mode__in=GameMode.objects.filter(
                description__icontains='capt'
            )
        )\
            .given(self.request)\
            .order_by('start_time')\
            .values('steam_id')

        limit = self.request.query_params.get(self.page_size_query_param)
        if limit is not None:
            result_limit = min(limit, self.max_page_size)
            matches = matches[:result_limit]
        else:
            matches = matches[:self.page_size]
        return matches

    def _get_pickban_queryset(self, matches):
        return Match.objects.filter(steam_id__in=matches)\
            .prefetch_related('pickban_set__hero')\
            .prefetch_related('pickban_set')\
            .values(
                'steam_id',
                'start_time',
                'radiant_win',
                'duration',
                'pickban__is_pick',
                'pickban__team',
                'pickban__order',
                'pickban__hero__steam_id',
        )

    def _refactor_pickbans(self, pickban_queryset):
        temp = {}
        for m in pickban_queryset:

            sid = m['steam_id']
            if sid not in temp:
                temp[sid] = {
                    'steam_id': sid,
                    'start_time': m['start_time'],
                    'radiant_win': m['radiant_win'],
                    'pickbans': []
                }
            temp[sid]['pickbans'].append(
                {
                    'hero': {'steam_id': m['pickban__hero__steam_id']},
                    'is_pick': m['pickban__is_pick'],
                    'team': m['pickban__team'],
                    'order': m['pickban__order'],
                }
            )

        return temp.values()

    def get_queryset(self):
        matches = self._get_matches()
        pickban_queryset = self._get_pickban_queryset(matches)
        data = self._refactor_pickbans(pickban_queryset)
        return data

global started
def started(sender, **kwargs):
    global started
    started = time.time()


def finished(sender, **kwargs):
    total = time.time() - started
    api_view_time = dispatch_time - (render_time + serializer_time + db_time)
    request_response_time = total - dispatch_time

    print ("Database lookup               | %.4fs" % db_time)
    print ("Serialization                 | %.4fs" % serializer_time)
    print ("Django request/response       | %.4fs" % request_response_time)
    print ("API view                      | %.4fs" % api_view_time)
    print ("Response rendering            | %.4fs" % render_time)

request_started.connect(started)
request_finished.connect(finished)


class PickBanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PickBan.objects.all()
    paginate_by = 10
    serializer_class = PickbanSerializer
    # filter_backends = (filters.SearchFilter,)
    # search_fields = ('name',)


class PlayerMatchSummaryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PlayerMatchSummarySerializer
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_queryset(self):
        queryset = PlayerMatchSummary.objects.given(self.request)

        limit = self.request.query_params.get(self.page_size_query_param)

        if limit is not None:
            result_limit = min(limit, self.max_page_size)
            queryset = queryset[:result_limit]
        else:
            queryset = queryset[:self.page_size]

        return queryset


class SkillBuildViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillBuildSerializer
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_queryset(self):
        queryset = SkillBuild.objects.all()

        match_id = self.request.query_params.get('match_id')
        if match_id is not None:
            queryset = queryset.filter(
                playermatchsummary__match__steam_id=match_id
            )
        else:
            queryset = queryset[:self.page_size]

        limit = self.request.query_params.get(self.page_size_query_param)
        if limit is not None:
            result_limit = min(limit, self.max_page_size)
            queryset = queryset[:result_limit]
        else:
            queryset = queryset[:self.page_size]

        return queryset
