""" Views for hero-related pages. """
from collections import defaultdict
from rest_framework import viewsets, filters

from django.views.generic import ListView, DetailView

from datadrivendota.views import ChartFormView, ApiView

from .models import Hero, Ability, HeroDossier, Role
from .serializers import HeroSerializer
from .mixins import (
    VitalsMixin,
    LineupMixin,
    HeroPerformanceMixin,
    HeroSkillProgressionMixin,
    HeroBuildLevelMixin,
    UpdatePlayerWinrateMixin,
    HeroPerformanceLineupMixin,
    HeroPickRateMixin,
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


"""
WARNING
EVERYTHING BELOW THIS IS DEPRECATED.
IT IS LEAVING SOON.
"""


class Vitals(VitalsMixin, ChartFormView):

    """ Hero vital stats chart. """

    title = "Hero Vitals"
    html = "heroes/form.html"

    def amend_params(self, chart):
        """ Do (no) chart editing. """
        return chart


class Lineup(LineupMixin, ChartFormView):

    """ Hero stat lineup chart. """

    title = "Hero Lineups"
    html = "heroes/form.html"

    def amend_params(self, chart):
        """ Tweak chart parameters. """
        chart.params.draw_legend = True
        chart.params.legendWidthPercent = .7
        chart.params.legendHeightPercent = .1
        return chart


class HeroPerformance(HeroPerformanceMixin, ChartFormView):

    """ Hero performance chart. """

    title = "Hero Performance"
    html = "heroes/form.html"

    def amend_params(self, chart):
        """ Edit chart display options. """
        chart.params.draw_legend = True
        chart.params.legendWidthPercent = .7
        chart.params.legendHeightPercent = .1
        return chart


class HeroSkillProgression(HeroSkillProgressionMixin, ChartFormView):

    """ Hero skill progression chart. """

    title = "Hero Skilling"
    html = "heroes/form.html"

    def amend_params(self, chart):
        """ Edit chart display options. """
        chart.params.path_stroke_width = 2
        return chart


class HeroBuildLevel(HeroBuildLevelMixin, ChartFormView):

    """ Hero build level chart. """

    title = "SkillBuild Winrate"
    html = "heroes/form.html"


class HeroPerformanceLineup(HeroPerformanceLineupMixin, ChartFormView):

    """ Hero performance chart. """

    title = "Hero Performance Lineup"
    html = "heroes/form.html"


class HeroPickBanLineup(HeroPickRateMixin, ChartFormView):

    """ Pick & Ban lineup. """

    title = "Hero Performance Lineup"
    html = "heroes/form.html"


# API endpoints
class ApiVitalsChart(VitalsMixin, ApiView):

    """ API chart. """

    pass


class ApiLineupChart(LineupMixin, ApiView):

    """ API chart. """

    pass


class ApiHeroPerformanceChart(HeroPerformanceMixin, ApiView):

    """ API chart. """

    pass


class ApiSkillProgressionChart(HeroSkillProgressionMixin, ApiView):

    """ API chart. """

    pass


class ApiBuildLevelChart(HeroBuildLevelMixin, ApiView):

    """ API chart. """

    pass


class ApiUpdatePlayerWinrateChart(UpdatePlayerWinrateMixin, ApiView):

    """ API chart. """

    pass


class ApiHeroPerformanceLineupChart(HeroPerformanceLineupMixin, ApiView):

    """ API chart. """

    pass
