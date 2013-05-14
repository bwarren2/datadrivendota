# Create your views here.
from django.shortcuts import get_object_or_404, render_to_response
from items.models import Item
from django.utils.text import slugify
from django.template import RequestContext
#from django.contrib.auth.decorators import login_required


def index(request):
    item_list = Item.objects.all().order_by('slug_name')
    print item_list
    return render_to_response('item_index.html', {'item_list': item_list},
                              context_instance=RequestContext(request))


def detail(request, item_name):
    item_slug = slugify(item_name)
    current_item = get_object_or_404(Item, slug_name=item_slug)

    return render_to_response('item_detail.html', {'item': current_item},
                              context_instance=RequestContext(request))
