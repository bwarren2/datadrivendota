from rest_framework import viewsets, filters
from rest_framework_extensions.cache.decorators import cache_response


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


class MatchPickBanViewSet(viewsets.ReadOnlyModelViewSet):
    page_size = 10
    page_size_query_param = 'page_size'
    serializer_class = FastMatchPickBansSerializer
    max_page_size = 200

    @cache_response()
    def retrieve(self, *args, **kwargs):
        return super(MatchPickBanViewSet, self).retrieve(*args, **kwargs)

    @cache_response()
    def list(self, *args, **kwargs):
        return super(MatchPickBanViewSet, self).list(*args, **kwargs)

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
            .prefetch_related('radiant_team__name')\
            .prefetch_related('dire_team__name')\
            .prefetch_related('pickban_set')\
            .values(
                'steam_id',
                'start_time',
                'radiant_win',
                'duration',
                'radiant_team__name',
                'dire_team__name',
                'pickban__is_pick',
                'pickban__team',
                'pickban__order',
                'pickban__hero__steam_id',
        ).order_by('start_time')

    def _refactor_pickbans(self, pickban_queryset):
        temp = {}
        for m in pickban_queryset:

            steam_id = m['steam_id']
            if steam_id not in temp:
                temp[steam_id] = {
                    'steam_id': steam_id,
                    'start_time': m['start_time'],
                    'radiant_team': m['radiant_team__name'],
                    'dire_team': m['dire_team__name'],
                    'duration': m['duration'],
                    'radiant_win': m['radiant_win'],
                    'pickbans': []
                }
            temp[steam_id]['pickbans'].append(
                {
                    'hero': {'steam_id': m['pickban__hero__steam_id']},
                    'is_pick': m['pickban__is_pick'],
                    'team': m['pickban__team'],
                    'order': m['pickban__order'],
                }
            )

        return sorted(temp.values(), key=lambda x: x['start_time'])

    def get_queryset(self):
        matches = self._get_matches()
        pickban_queryset = self._get_pickban_queryset(matches)
        data = self._refactor_pickbans(pickban_queryset)
        return data


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

    @cache_response()
    def retrieve(self, *args, **kwargs):
        return super(PlayerMatchSummaryViewSet, self).retrieve(*args, **kwargs)

    @cache_response()
    def list(self, *args, **kwargs):
        return super(PlayerMatchSummaryViewSet, self).list(*args, **kwargs)

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
