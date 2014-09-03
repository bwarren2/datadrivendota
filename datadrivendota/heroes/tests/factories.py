import factory

from django.utils.text import slugify

from heroes.models import Hero


class HeroFactory(factory.django.DjangoModelFactory):
    FACTORY_FOR = Hero

    name = factory.Sequence(lambda n: 'Hero{0}'.format(n))
    machine_name = factory.Sequence(lambda n: 'hero{0}'.format(n))
    internal_name = factory.LazyAttribute(lambda obj: slugify(obj.name))
    steam_id = factory.Sequence(lambda n: n + 1)
    lore = 'my lore'
    visible = True
