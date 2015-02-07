from django.db import models
from django.db.models import Count
from django.conf import settings


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
            .filter(steam_id__in=settings.TI4_TEAMS)
        return qs
