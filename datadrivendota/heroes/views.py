""" Views for hero-related pages. """
from collections import defaultdict
from rest_framework import viewsets, filters

from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import When, Case, Value, IntegerField, Sum

from matches.models import PlayerMatchSummary, PickBan
from .models import Hero, Ability, HeroDossier, Role
from .serializers import (
    HeroSerializer,
    HeroDossierSerializer,
    HeroWinrateSerializer,
    HeroPickBanSerializer
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

        # TODO Temporary for testing. Put this where you actually want the
        # control bar to show.
        kwargs['show_control_bar'] = True

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


class HeroWinrateViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero winrate endpoint. """

    paginate_by = None
    serializer_class = HeroWinrateSerializer

    def get_queryset(self):

        data_queryset = PlayerMatchSummary.objects.given(self.request)

        data_queryset = data_queryset.values('hero__steam_id')\
            .order_by()\
            .annotate(
                wins=Sum(
                    Case(
                        When(is_win=True, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                losses=Sum(
                    Case(
                        When(is_win=False, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                games=Sum(
                    Case(
                        default=Value(1),
                        output_field=IntegerField()
                    )
                )
        )

        return data_queryset


class HeroPickBanViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero pickban endpoint. """

    paginate_by = None
    serializer_class = HeroPickBanSerializer

    def get_queryset(self):

        data_queryset = PickBan.objects.given(self.request)

        data_queryset = data_queryset.values('hero__steam_id')\
            .order_by()\
            .annotate(
                picks=Sum(
                    Case(
                        When(is_pick=True, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                bans=Sum(
                    Case(
                        When(is_pick=False, then=1),
                        default=Value(0),
                        output_field=IntegerField()
                    )
                ),
                pick_or_bans=Sum(
                    Case(
                        default=Value(1),
                        output_field=IntegerField()
                    )
                )
        )
        return data_queryset


class HeroDossierViewSet(viewsets.ReadOnlyModelViewSet):

    """ DRF hero endpoint. """

    queryset = HeroDossier.objects.all()
    paginate_by = None
    serializer_class = HeroDossierSerializer


class VitalsView(TemplateView):
    template_name = 'heroes/vitals.html'


class LineupView(TemplateView):
    template_name = 'heroes/lineups.html'
