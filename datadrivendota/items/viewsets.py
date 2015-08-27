from rest_framework import viewsets, filters
from .serializers import ItemSerializer

from items.models import Item


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'steam_id'
    paginate_by = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
