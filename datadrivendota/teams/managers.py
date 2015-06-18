from django.db import models
from django.db.models import Count


class SortedTeamManager(models.Manager):

    def get_queryset(self):
        qs = super(SortedTeamManager, self)\
            .get_queryset()\
            .exclude(name=None)\
            .annotate(Count('radiant_team')).order_by('-radiant_team__count')
        return qs


class TI4TeamManager(models.Manager):

    def get_queryset(self):
        qs = super(TI4TeamManager, self).get_queryset()\
            .filter(steam_id__in=[
                1333179,
                999689,
                15,
                26,
                5,
                7,
                726228,
                39,
                111474,
                36,
                350190,
                46,
                26,
                1375614,
                1642908,
            ]
        )
        return qs
