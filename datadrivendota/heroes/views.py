""" Views for hero-related pages. """
from collections import defaultdict
from rest_framework import viewsets, filters

from django.views.generic import ListView, DetailView, TemplateView

from datadrivendota.views import ApiView

from .models import Hero, Ability, HeroDossier, Role
from .serializers import HeroSerializer, HeroDossierSerializer
from .mixins import (
    VitalsMixin,
    LineupMixin,
    HeroPerformanceMixin,
    HeroSkillProgressionMixin,
    HeroBuildLevelMixin,
    UpdatePlayerWinrateMixin,
    HeroPerformanceLineupMixin,
)


class IndexView(ListView):

    """Return all the heroes.  @TODO: Clean up the role markup step."""

    queryset = Hero.objects.filter(visible=True).order_by('name')

    def get_context_data(self, **kwargs):
        """
        Fetch the heroes and roles lists.

        We want to mark up the heroes with their roles for interactive display.
        We do some monkeying with
        """
        a = self.queryset.values_list('steam_id', 'assignment__role__name')

        ddct = defaultdict(list)
        for pair in a:
            id, role = pair
            if role is not None:
                ddct[id].append(role)
        ddct = {a: " ".join(b) for a, b in ddct.iteritems()}

        for hero in self.object_list:
            hero.classes = ddct.get(hero.steam_id, "")

        kwargs['hero_list'] = self.object_list
        kwargs['role_list'] = Role.objects.all().select_related()

        return super(IndexView, self).get_context_data(**kwargs)


class HeroDetailView(DetailView):

    """ Take a name, get a hero. """

    queryset = Hero.public.all()
    slug_field = 'machine_name'
    slug_url_kwarg = 'hero_name'

    def get_context_data(self, **kwargs):
        """ Add in abilities and dossier. """
        kwargs['abilities'] = Ability.objects.filter(
            is_core=True,
            hero=self.object
        ).order_by('steam_id')
        kwargs['dossier'] = HeroDossier.objects.get(hero=self.object)
        return super(HeroDetailView, self).get_context_data(**kwargs)


class AbilityDetailView(DetailView):

    """ Display details of an ability. """

    queryset = Ability.objects.all()
    slug_field = 'machine_name'
    slug_url_kwarg = 'ability_name'


class HeroViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero endpoint. """

    queryset = Hero.objects.all()
    paginate_by = None
    serializer_class = HeroSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class HeroDossierViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero endpoint. """

    queryset = HeroDossier.objects.all()
    paginate_by = None
    serializer_class = HeroDossierSerializer


class VitalsView(TemplateView):
    template_name = 'heroes/vitals.html'


class LineupView(TemplateView):
    template_name = 'heroes/lineups.html'


# API endpoints
class ApiVitalsChart(VitalsMixin, ApiView):
    pass


class ApiLineupChart(LineupMixin, ApiView):
    pass


class ApiHeroPerformanceChart(HeroPerformanceMixin, ApiView):
    pass


class ApiSkillProgressionChart(HeroSkillProgressionMixin, ApiView):
    pass


class ApiBuildLevelChart(HeroBuildLevelMixin, ApiView):
    pass


class ApiUpdatePlayerWinrateChart(UpdatePlayerWinrateMixin, ApiView):
    pass


class ApiHeroPerformanceLineupChart(HeroPerformanceLineupMixin, ApiView):
    pass
