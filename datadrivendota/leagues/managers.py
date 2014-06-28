from django.db import models
from django.db.models import Max


class SortedLeagueManager(models.Manager):

    def get_queryset(self):
        qs = super(SortedLeagueManager, self).get_queryset()\
            .annotate(Max('match__start_time'))\
            .exclude(steam_id=0)\
            .order_by('-match__start_time__max')\
            .exclude(match__start_time__max=None)
        return qs
