from django.contrib.syndication.views import Feed
from .models import Entry


class EntryFeed(Feed):
    title = 'Blog Entries'
    link = '/entries/'
    description = "News from DataDrivenDota"

    def items(self):
        return Entry.public.all().order_by('-created')[:5]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description
