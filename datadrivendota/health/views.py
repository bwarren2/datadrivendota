from django.views.generic import TemplateView
from django.conf import settings
from datadrivendota.mixins import SuperuserRequiredMixin
from matches.models import Match, PlayerMatchSummary
from players.models import Player
from heroes.models import Hero


class HealthIndexView(SuperuserRequiredMixin, TemplateView):
    template_name = 'health_index.html'

    def get_context_data(self, **kwargs):
        kwargs['read_key'] = settings.KEEN_READ_KEY
        kwargs['project_id'] = settings.KEEN_PROJECT_ID
        return super(HealthIndexView, self).get_context_data(**kwargs)


class CardIndexView(SuperuserRequiredMixin, TemplateView):
    template_name = 'card_index.html'

    def get_context_data(self, **kwargs):
        kwargs['hero'] = Hero.public.all().select_related().order_by('?')[0]
        kwargs['match'] = Match.objects.all().select_related()\
            .order_by('-start_time')[0]
        kwargs['summary'] = PlayerMatchSummary.objects.all().select_related()\
            .order_by('-id')[0]
        kwargs['player'] = Player.objects.filter(updated=True)\
            .select_related()[0]
        return super(CardIndexView, self).get_context_data(**kwargs)


class StylesIndexView(SuperuserRequiredMixin, TemplateView):
    template_name = 'bootstrap_test.html'
