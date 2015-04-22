from random import choice
from rest_framework import viewsets, filters

from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView


from datadrivendota.mixins import SubscriberRequiredMixin
from datadrivendota.views import ChartFormView, ApiView


from .mixins import (
    WinrateMixin,
    HeroAdversaryMixin,
    HeroAbilitiesMixin,
    VersusWinrateMixin,
    RoleMixin,
    )
from .models import Player
from heroes.models import Hero
from .serializers import PlayerSerializer


class PlayerIndexView(ListView):
    queryset = Player.objects.filter(updated=True)


class FollowedPlayerIndexView(SubscriberRequiredMixin, ListView):

    def get_queryset(self):
        return self.request.user.userprofile.following.all()


class ProIndexView(ListView):
    queryset = Player.TI4.all()


class PlayerDetailView(DetailView):
    model = Player
    slug_url_kwarg = 'player_id'
    slug_field = 'steam_id'

    def get_context_data(self, **kwargs):

        kwargs['player'] = self.object
        kwargs['pms_list'] = self.object.summaries(36)

        p2s = Player.objects.exclude(pro_name=None,)\
            .exclude(steam_id=self.object.steam_id,)

        try:
            p2 = choice([p for p in p2s])

            kwargs['compare_url'] = reverse(
                'players:comparison',
                kwargs={
                    'player_id_1': self.object.steam_id,
                    'player_id_2': p2.steam_id,
                })
            kwargs['compare_str'] = 'Compare {p1} to {p2}!'.format(
                p1=self.object.display_name,
                p2=p2.display_name,
            )
        except IndexError:
            # If there are no other players, like in tests, this is not a breaking requirement.
            pass

        stats = {}
        stats['wins'] = self.object.wins
        stats['losses'] = self.object.losses
        stats['total'] = self.object.games
        stats['winrate'] = round(
            float(stats['wins']) / (stats['wins'] + stats['losses'])*100 \
                if stats['wins'] + stats['wins'] > 0 else 0, 2
        )
        kwargs['stats'] = stats

        # Compare to dendi and s4 by default
        player_list = [70388657, 41231571, self.object.steam_id]
        endgame_players = Player.objects.filter(steam_id__in=player_list)
        kwargs['player_ids'] = ",".join(
            [str(p.steam_id) for p in endgame_players]
        )

        return super(PlayerDetailView, self).get_context_data(**kwargs)


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    lookup_field = 'steam_id'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('persona_name',)


class Winrate(WinrateMixin, ChartFormView):
    title = "Hero Winrate"
    html = "players/form.html"


class HeroAdversary(HeroAdversaryMixin, ChartFormView):
    title = "Player Hero Adversary"
    html = "players/form.html"


class HeroAbilities(HeroAbilitiesMixin, ChartFormView):
    title = "Hero Skilling Comparison"
    html = "players/form.html"

    def amend_params(self, chart):
        chart.params.path_stroke_width = 1
        return chart


class PlayerComparsionView(TemplateView):
    template_name = 'players/comparison.html'

    def get_context_data(self, **kwargs):
        kwargs['player_1'] = get_object_or_404(
            Player, steam_id=kwargs['player_id_1']
        )
        kwargs['player_2'] = get_object_or_404(
            Player, steam_id=kwargs['player_id_2']
        )


class HeroStyleView(TemplateView):
    # So much magic in the template!
    template_name = 'players/hero_style.html'

    def get_context_data(self, **kwargs):
        kwargs['player'] = get_object_or_404(
            Player, steam_id=kwargs['player_id']
            )
        kwargs['hero'] = get_object_or_404(
            Hero, machine_name=kwargs['hero_name']
        )


class ApiWinrateChart(WinrateMixin, ApiView):
    pass


class ApiHeroAdversary(HeroAdversaryMixin, ApiView):
    pass


class ApiHeroAbilities(HeroAbilitiesMixin, ApiView):
    pass


class ApiVersusWinrate(VersusWinrateMixin, ApiView):
    pass


class ApiRole(RoleMixin, ApiView):
    pass
