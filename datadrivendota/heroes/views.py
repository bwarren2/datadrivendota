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
    """
    Return all the heroes.  @TODO: Clean up the role markup step.
    """
    queryset = Hero.objects.filter(visible=True).order_by('name')

    def get_context_data(self, **kwargs):
        """
        Fetches the heroes and roles lists

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
    """
    Take a name, get a hero.
    """
    queryset = Hero.public.all()
    slug_field = 'machine_name'
    slug_url_kwarg = 'hero_name'

    def get_context_data(self, **kwargs):
        kwargs['abilities'] = Ability.objects.filter(
            is_core=True,
            hero=self.object
        ).order_by('steam_id')
        kwargs['dossier'] = HeroDossier.objects.get(hero=self.object)
        return super(HeroDetailView, self).get_context_data(**kwargs)


class AbilityDetailView(DetailView):
    queryset = Ability.objects.all()
    slug_field = 'machine_name'
    slug_url_kwarg = 'ability_name'


class HeroViewSet(viewsets.ReadOnlyModelViewSet):
    """
    DRF hero endpoint
    """
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
    title = "Hero Vitals"
    html = "heroes/form.html"

    def amend_params(self, chart):
        return chart


class Lineup(LineupMixin, ChartFormView):
    title = "Hero Lineups"
    html = "heroes/form.html"

    def amend_params(self, chart):
        chart.params.draw_legend = True
        chart.params.legendWidthPercent = .7
        chart.params.legendHeightPercent = .1
        return chart


class HeroPerformance(HeroPerformanceMixin, ChartFormView):
    title = "Hero Performance"
    html = "heroes/form.html"

    def amend_params(self, chart):
        chart.params.draw_legend = True
        chart.params.legendWidthPercent = .7
        chart.params.legendHeightPercent = .1
        return chart


class HeroSkillProgression(HeroSkillProgressionMixin, ChartFormView):
    title = "Hero Skilling"
    html = "heroes/form.html"

    def amend_params(self, chart):
        chart.params.path_stroke_width = 2
        return chart


class HeroBuildLevel(HeroBuildLevelMixin, ChartFormView):
    title = "SkillBuild Winrate"
    html = "heroes/form.html"


class HeroPerformanceLineup(HeroPerformanceLineupMixin, ChartFormView):
    title = "Hero Performance Lineup"
    html = "heroes/form.html"

class HeroPickBanLineup(HeroPickRateMixin, ChartFormView):
    title = "Hero Performance Lineup"
    html = "heroes/form.html"


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
