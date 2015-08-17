from rest_framework import viewsets, filters

from .serializers import TeamSerializer
from .models import Team


class TeamViewSet(viewsets.ReadOnlyModelViewSet):

    """ List and detail for teams. """

    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    paginate_by = 10
