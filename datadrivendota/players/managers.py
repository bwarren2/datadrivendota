from django.db import models
from teams.models import assemble_pros, TeamDossier


class TI4Manager(models.Manager):

    def get_queryset(self):
        teams = TeamDossier.TI4.filter()
        id_lst = assemble_pros(teams)
        qs = super(TI4Manager, self).get_queryset()\
            .filter(steam_id__in=id_lst)\
            .order_by('pro_name')
        return qs
