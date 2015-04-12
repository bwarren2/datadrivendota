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
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero winrate for a particular player."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Modes and players you want to see here.  (Hint: don't use ability draft.)"
        },
        {
            'element': "ul.nav-tabs",
            'title': "Other questions",
            'content': "For other charts, like endgame data for individuals, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: Who is Dendi's highest winrate hero of those with 15 games?"
        }
    ]
    title = "Hero Winrate"
    html = "players/form.html"


class HeroAdversary(HeroAdversaryMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts hero adversarial performance."
        },
    ]
    title = "Player Hero Adversary"
    html = "players/form.html"


class HeroAbilities(HeroAbilitiesMixin, ChartFormView):
    tour = [
        {
            'orphan': True,
            'title': "Welcome!",
            'content': "This page charts in-game level progression for two players."
        },
        {
            'orphan': True,
            'title': "Example",
            'content': "For example, you can compare Dendi's Pudge to XBOCT's Lifestealer."
        },
        {
            'element': ".chart-form",
            'title': "Asking questions",
            'content': "Pick two players and two heroes to compare their leveling rates."
        },
        {
            'element': "#main-nav",
            'title': "Other questions",
            'content': "For other charts, like data about heroes stats, try other tabs.",
            'placement': "bottom"
        },
        {
            'orphan': True,
            'title': "Ready to go!",
            'content': "Challenge: At what level does Dendi's Pudge start falling behind Funnik's Lifestealer?"
        }
    ]
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
