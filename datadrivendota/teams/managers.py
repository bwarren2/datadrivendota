from django.db import models
from django.db.models import Count


class SortedTeamManager(models.Manager):

    def get_queryset(self):
        qs = super(SortedTeamManager, self).get_queryset()\
            .select_related('teamdossier')\
            .annotate(Count('radiant_team')).order_by('-radiant_team__count')
        return qs
