from rest_framework import viewsets, filters
from .serializers import ItemSerializer
from django.views.generic import ListView, DetailView

from items.models import Item
from datadrivendota.views import ApiView
from .mixins import ItemWinrateMixin


class ItemIndex(ListView):
    queryset = Item.objects.exclude(cost=0).order_by('slug_name')


class ItemDetailView(DetailView):
    queryset = Item.objects.exclude(cost=0).order_by('slug_name')
    slug_field = 'slug_name'
    slug_url_kwarg = 'item_name'


class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'steam_id'
    paginate_by = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


"""
EVERYTHING BELOW HERE IS DEPRECATED

YOU ARE WARNED.
"""

class ApiItemEndgameChart(ItemWinrateMixin, ApiView):
    pass
