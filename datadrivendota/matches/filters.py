import time

from django.db.models import F

import django_filters
from rest_framework import filters

from .models import Match


class MatchFilter(filters.FilterSet):
    player = django_filters.MethodFilter()
    hero = django_filters.MethodFilter()

    def get_associated_value(self, value_name):
        return self.form.data.get(value_name)

    def filter_player(self, queryset, value):
        if value:
            hero = self.get_associated_value('hero')
            if hero:
                queryset = queryset.filter(
                    playermatchsummary__player__persona_name=value,
                    playermatchsummary__hero__name=hero,
                )
            else:
                queryset = queryset.filter(
                    playermatchsummary__player__persona_name=value,
                )
        return queryset

    def filter_hero(self, queryset, value):
        if value:
            player = self.get_associated_value('player')
            if player:
                queryset = queryset.filter(
                    playermatchsummary__player__persona_name=player,
                    playermatchsummary__hero__name=value,
                )
            else:
                queryset = queryset.filter(
                    playermatchsummary__hero__name=value,
                )
        return queryset

    league = django_filters.CharFilter(
        name='league__name',
    )
    radiant_team = django_filters.CharFilter(
        name='radiant_team__name',
    )
    dire_team = django_filters.CharFilter(
        name='dire_team__name',
    )
    start_date = django_filters.MethodFilter()
    end_date = django_filters.MethodFilter()

    @staticmethod
    def date_to_epoch(value):
        pattern = '%Y-%m-%d'
        return int(time.mktime(time.strptime(value, pattern)))

    def filter_start_date(self, queryset, value):
        if value:
            epoch = self.date_to_epoch(value)
            queryset = queryset.filter(start_time__gte=epoch)
        return queryset

    def filter_end_date(self, queryset, value):
        if value:
            epoch = self.date_to_epoch(value)
            queryset = queryset.annotate(
                end_time=F('start_time') + F('duration'),
            ).filter(
                end_time__lte=epoch,
            )
        return queryset

    class Meta:
        model = Match
        fields = (
            'player',
            'hero',
            'league',
            'radiant_team',
            'dire_team',
            'start_date',
            'end_date',
        )
