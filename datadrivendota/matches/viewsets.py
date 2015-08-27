from rest_framework import viewsets, filters

from .models import Match, PlayerMatchSummary, PickBan, SkillBuild, GameMode

from .serializers import (
    MatchSerializer,
    PlayerMatchSummarySerializer,
    SkillBuildSerializer,
    MatchPickBansSerializer,
    PickbanSerializer,
)


class MatchViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 200

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


class MatchPickBanViewSet(viewsets.ReadOnlyModelViewSet):
    page_size = 10
    page_size_query_param = 'page_size'
    serializer_class = MatchPickBansSerializer
    max_page_size = 200

    def get_queryset(self):
        queryset = Match.objects.filter(
            game_mode__in=GameMode.objects.filter(
                description__icontains='capt'
            )
        )\
            .prefetch_related('pickban_set__hero')\
            .prefetch_related('pickban_set')\
            .given(self.request)\
            .order_by('start_time')

        limit = self.request.query_params.get(self.page_size_query_param)

        if limit is not None:
            result_limit = min(limit, self.max_page_size)
            queryset = queryset[:result_limit]
        else:
            queryset = queryset[:self.page_size]

        return queryset.select_related()


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
