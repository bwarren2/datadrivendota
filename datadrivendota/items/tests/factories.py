from factory.django import DjangoModelFactory
from factory import SubFactory, Sequence, LazyAttribute
from factory.fuzzy import FuzzyInteger, FuzzyChoice

from django.utils.text import slugify

from items.models import (
    Item,
)


class ItemFactory(DjangoModelFactory):
    class Meta:
        model = Item

    steam_id = Sequence(lambda n: n + 1)
    name = Sequence(lambda n: u'Item{0}'.format(n))
    internal_name = LazyAttribute(lambda obj: slugify(obj.name))
    quality = Sequence(lambda n: u'Quality{0}'.format(n))

    cost = FuzzyInteger(0, 5000)
    description = Sequence(lambda n: u'Description{0}'.format(n))
    notes = Sequence(lambda n: u'Description{0}'.format(n))
    mana_cost = FuzzyInteger(0, 5000)
    cooldown = FuzzyInteger(0, 5000)
    lore = Sequence(lambda n: u'Lore{0}'.format(n))
    created = FuzzyChoice([True, False, None])
    slug_name = Sequence(lambda n: u'Slug{0}'.format(n))


class ItemAttributes(DjangoModelFactory):
    item = SubFactory(ItemFactory)
    attribute = Sequence(lambda n: u'Ingredient{0}'.format(n))


class ItemComponents(DjangoModelFactory):
    product = SubFactory(ItemFactory)
    ingredient = SubFactory(ItemFactory)
