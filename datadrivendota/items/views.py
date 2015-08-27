from django.views.generic import ListView, DetailView

from items.models import Item


class ItemIndex(ListView):
    queryset = Item.objects.exclude(cost=0).order_by('slug_name')


class ItemDetailView(DetailView):
    queryset = Item.objects.exclude(cost=0).order_by('slug_name')
    slug_field = 'slug_name'
    slug_url_kwarg = 'item_name'
