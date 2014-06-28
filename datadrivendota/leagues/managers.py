from django.db import models
from django.db.models import Max


class SortedLeagueManager(models.Manager):

    def get_queryset(self):
        qs = super(SortedLeagueManager, self).get_queryset()\
            .annotate(Max('match__start_time'))\
            .exclude(match__start_time__max=None)\
            .order_by('-match__start_time__max')
        return qs
