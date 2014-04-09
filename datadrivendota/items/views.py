from django.shortcuts import get_object_or_404, render
from items.models import Item
from django.utils.text import slugify

from datadrivendota.views import FormView
from .json_data import item_endgame
from .forms import ItemWinrateForm


def index(request):
    item_list = Item.objects.exclude(cost=0).order_by('slug_name')
    return render(request, 'items/index.html', {'item_list': item_list})


def detail(request, item_name):
    item_slug = slugify(item_name)
    current_item = get_object_or_404(Item, slug_name=item_slug)
    return render(request, 'items/detail.html', {'item': current_item})


class ItemWinrateView(FormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts item usage for a player on a hero."
        },
        ]

    form = ItemWinrateForm
    attrs = ['hero', 'player', 'game_modes']
    json_function = staticmethod(item_endgame)
    title = "Item Winrate"
    html = "items/form.html"

    def amend_params(self, params):
        params['draw_legend'] = False
        return params
