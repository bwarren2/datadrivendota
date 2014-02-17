from django.shortcuts import get_object_or_404, render
from items.models import Item
from django.utils.text import slugify
from django.contrib.auth.decorators import permission_required


@permission_required('players.can_look')
def index(request):
    item_list = Item.objects.exclude(cost=0).order_by('slug_name')
    return render(request, 'items/index.html', {'item_list': item_list})


@permission_required('players.can_look')
def detail(request, item_name):
    item_slug = slugify(item_name)
    current_item = get_object_or_404(Item, slug_name=item_slug)
    return render(request, 'items/detail.html', {'item': current_item})
