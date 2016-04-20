import json
from django.conf import settings
from django.db import models
from django.db.models import Q


class MatchFilteredQuerySet(models.QuerySet):

    filter_pipeline = None  # A list of functions to winnow the queryset

    def __init__(self, *args, **kwargs):
        super(MatchFilteredQuerySet, self).__init__(*args, **kwargs)
        self.filter_pipeline = [
            self.filter_ids,
            self.filter_hero,
            self.filter_league,
            self.filter_team,
            self.filter_skill,
            self.filter_validity,
            self.filter_match,
            self.filter_start_time_gte,
            self.filter_start_time_lte,
        ]

    def given(self, request):
        """ Filter the query set based on request parameter. """
        self.request = request
        queryset = self

        try:
            for filter_fn in self.filter_pipeline:
                queryset = filter_fn(queryset)
            return queryset

        except ValueError:
            return queryset.none()

    def filter_ids(self, queryset):
        try:
            ids = json.loads(self.request.query_params.get('ids'))
            if ids is not None:
                queryset = queryset.filter(id__in=ids)
            return queryset

        except TypeError:
            # no parameter named ids
            return queryset

    def filter_validity(self, queryset):
        valid = self.request.query_params.get('validity')
        if valid is not None:
            if valid == 'LEGIT':
                # hardcoding to dodge circular import
                queryset = queryset.filter(match__validity=1)
            elif valid == 'ALL':
                pass
            else:
                pass

        return queryset

    def filter_hero(self, queryset):

        hero = self.request.query_params.get('hero_id')
        if hero is not None:
            queryset = queryset.filter(hero__steam_id=hero)

        return queryset

    def filter_league(self, queryset):

        league = self.request.query_params.get('league_id')
        if league is not None:
            queryset = queryset.filter(match__league__steam_id=league)

        return queryset

    def filter_skill(self, queryset):

        skill = self.request.query_params.get('skill')
        if skill is not None:
            queryset = queryset.filter(match__skill=skill)

        return queryset

    def filter_team(self, queryset):

        team = self.request.query_params.get('team_id')
        if team is not None:
            queryset = queryset.filter(
                Q(match__radiant_team__steam_id=team) |
                Q(match__dire_team__steam_id=team)
            )

        return queryset

    def filter_match(self, queryset):

        match = self.request.query_params.get('match_id')
        if match is not None:
            match = int(match)
            queryset = queryset.filter(
                match__steam_id=match
            )

        return queryset

    def filter_start_time_gte(self, queryset):

        cutoff = self.request.query_params.get('start_time_gte')
        if cutoff is not None:
            queryset = queryset.filter(
                match__start_time__gte=cutoff
            )

        return queryset

    def filter_start_time_lte(self, queryset):

        cutoff = self.request.query_params.get('start_time_lte')
        if cutoff is not None:
            queryset = queryset.filter(
                match__start_time__lte=cutoff
            )

        return queryset


class PMSQuerySet(MatchFilteredQuerySet):

    def __init__(self, *args, **kwargs):
        super(PMSQuerySet, self).__init__(*args, **kwargs)
        self.filter_pipeline.append(self.filter_player)

    def filter_player(self, queryset):
        player = self.request.query_params.get('player_id')
        if player is not None:
            queryset = queryset.filter(player__steam_id=player)

        return queryset


class FilteredQuerySet(models.QuerySet):

    filter_pipeline = None  # A list of functions to winnow the queryset

    def __init__(self, *args, **kwargs):
        super(FilteredQuerySet, self).__init__(*args, **kwargs)
        self.filter_pipeline = [
            self.filter_ids,
            self.filter_league,
            self.filter_team,
            self.filter_skill,
            self.filter_validity,
            self.filter_match,
            self.filter_start_time_lte,
            self.filter_start_time_gte,
        ]

    def given(self, request):
        """ Filter the query set based on request parameter. """
        self.request = request
        queryset = self

        try:
            for filter_fn in self.filter_pipeline:
                queryset = filter_fn(queryset)
            return queryset

        except ValueError:
            return queryset.none()

    def filter_validity(self, queryset):
        valid = self.request.query_params.get('validity')
        if valid is not None:
            if valid == 'LEGIT':
                # hardcoding to dodge circular import
                queryset = queryset.filter(validity=1)
            elif valid == 'ALL':
                pass
            else:
                pass

        return queryset

    def filter_league(self, queryset):

        league = self.request.query_params.get('league_id')
        if league is not None:
            queryset = queryset.filter(league__steam_id=league)

        return queryset

    def filter_skill(self, queryset):

        skill = self.request.query_params.get('skill')
        if skill is not None:
            queryset = queryset.filter(skill=skill)

        return queryset

    def filter_team(self, queryset):

        team = self.request.query_params.get('team_id')
        if team is not None:
            queryset = queryset.filter(
                Q(radiant_team__steam_id=team) |
                Q(dire_team__steam_id=team)
            )

        return queryset

    def filter_match(self, queryset):

        match = self.request.query_params.get('match_id')
        if match is not None:
            match = int(match)
            queryset = queryset.filter(
                steam_id=match
            )

        return queryset

    def filter_start_time_gte(self, queryset):

        cutoff = self.request.query_params.get('start_time_gte')
        if cutoff is not None:
            queryset = queryset.filter(
                start_time__gte=cutoff
            )

        return queryset

    def filter_start_time_lte(self, queryset):

        cutoff = self.request.query_params.get('start_time_lte')
        if cutoff is not None:
            queryset = queryset.filter(
                start_time__lte=cutoff
            )

        return queryset

    def filter_ids(self, queryset):
        try:
            ids = json.loads(self.request.query_params.get('ids'))
            print ids
            if ids is not None:
                queryset = queryset.filter(id__in=ids)
            return queryset

        except TypeError:
            # no parameter named ids
            return queryset


class Unparsed(FilteredQuerySet):

    def get_queryset(self):
        return super(Unparsed, self).get_queryset().exclude(
            parsed_with=settings.PARSER_VERSION
        )


class Parsed(FilteredQuerySet):

    def get_queryset(self):
        return super(Parsed, self).get_queryset().filter(
            parsed_with=settings.PARSER_VERSION
        )
