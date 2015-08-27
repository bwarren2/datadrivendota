
from rest_framework import viewsets, filters

from .models import League
from .serializers import LeagueSerializer


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    paginate_by = 10
