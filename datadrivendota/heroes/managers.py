from django.db import models


class VisibleHeroManager(models.Manager):

    def get_queryset(self):
        qs = super(VisibleHeroManager, self).get_queryset()\
            .exclude(visible=False)
        return qs
