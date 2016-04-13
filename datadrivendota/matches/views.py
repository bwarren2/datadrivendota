from django.views.generic import DetailView, ListView, TemplateView
from utils.views import ability_infodict
from django.contrib import messages
from parserpipe.models import MatchRequest

from .models import Match, PlayerMatchSummary, PickBan
from utils.pagination import SmarterPaginator


class MatchDetail(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'

    def get_context_data(self, **kwargs):
        if self.request.user.is_superuser:
            try:
                kwargs['matchrequest'] = MatchRequest.objects.get(
                    match_id=self.object.steam_id
                )
                kwargs['clearname'] = dict(MatchRequest.STATUS_CHOICES)[
                    kwargs['matchrequest'].status
                ]
            except MatchRequest.DoesNotExist:
                # Not a parsed match
                kwargs['clearname'] = 'Unparsed'

        return super(MatchDetail, self).get_context_data(**kwargs)


class MatchDetailPickban(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/match_pickbans.html'

    def get_context_data(self, **kwargs):

        try:
            # Magic numbers are bad, but 0 = radiant.  Fix later
            dire_picks = PickBan.objects.filter(
                match=self.object,
                team=1,
                is_pick=True
            ).select_related('hero')

            dire_bans = PickBan.objects.filter(
                match=self.object,
                team=1,
                is_pick=False
            ).select_related('hero')

            radiant_picks = PickBan.objects.filter(
                match=self.object,
                is_pick=True
            ).exclude(team=1).select_related('hero')

            radiant_bans = PickBan.objects.filter(
                match=self.object,
                is_pick=False
            ).exclude(team=1).select_related('hero')

            pickban_length = (
                dire_picks.count() +
                dire_bans.count() +
                radiant_picks.count() +
                radiant_bans.count()
            )

            kwargs['dire_picks'] = dire_picks
            kwargs['dire_bans'] = dire_bans
            kwargs['radiant_picks'] = radiant_picks
            kwargs['radiant_bans'] = radiant_bans
            kwargs['pickban_length'] = pickban_length

        except IndexError:
            raise
        finally:
            return super(MatchDetailPickban, self).get_context_data(**kwargs)


class MatchDetailAbilities(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/match_abilities.html'

    def get_context_data(self, **kwargs):
        kwargs['match'] = self.object
        summaries = PlayerMatchSummary.objects.filter(
            match=self.object
        ).select_related().order_by('player_slot')

        radiant_summaries = [
            summary for summary in summaries if summary.side == 'Radiant'
        ]
        radiant_infodict = {}
        for summary in radiant_summaries:
            radiant_infodict[summary.player_slot] = ability_infodict(summary)
        kwargs['radiant_infodict'] = radiant_infodict

        dire_summaries = [
            summary for summary in summaries if summary.side == 'Dire'
        ]
        dire_infodict = {}
        for summary in dire_summaries:
            dire_infodict[summary.player_slot] = ability_infodict(summary)
        kwargs['dire_infodict'] = dire_infodict

        return super(MatchDetailAbilities, self).get_context_data(**kwargs)


class MatchDetailScorecard(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/match_scorecard.html'

    def get_context_data(self, **kwargs):
        kwargs['match'] = self.object
        summaries = PlayerMatchSummary.objects.filter(
            match=self.object
        ).select_related().order_by('player_slot')

        kwargs['summaries'] = summaries
        return super(MatchDetailScorecard, self).get_context_data(**kwargs)


class MatchParsedDetail(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/match_parsed_detail.html'


class TimeLapseView(TemplateView):
    template_name = 'matches/time_lapse.html'


class DuelView(TemplateView):
    template_name = 'matches/duel.html'


class GhostWalkView(TemplateView):
    template_name = 'matches/ghostwalk.html'

    def get_context_data(self, **kwargs):
        kwargs['show_control_bar'] = True
        return super(GhostWalkView, self).get_context_data(**kwargs)


class ReplayView(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'
    template_name = 'matches/replay.html'

    def get_context_data(self, **kwargs):
        kwargs['show_control_bar'] = True

        messages.success(
            self.request,
            'This section is very data intensive tech still in development; it can take up to a minute to load, based on your connection. '
        )

        return super(ReplayView, self).get_context_data(**kwargs)


class PerformanceView(TemplateView):
    template_name = 'matches/performance.html'


class MatchListView(ListView):
    queryset = Match.objects.all()
    paginate_by = 10

    def get_queryset(self):
        qs = super(MatchListView, self).get_queryset()
        filter_league = self.request.GET.get('league_id', None)

        if filter_league:
            matches = qs.filter(
                league__steam_id=filter_league,
                validity=Match.LEGIT
            )
        else:
            matches = qs.filter(
                validity=Match.LEGIT
            )

        matches = matches.select_related(
                'radiant_team',
                'dire_team',
                'league',
            ).prefetch_related(
                'playermatchsummary_set',
                'playermatchsummary_set__hero',
                'playermatchsummary_set__player',
                'playermatchsummary_set__leaver',
            )
        return matches

    def paginate_queryset(self, queryset, page_size):
        page = self.request.GET.get('page')
        paginator = SmarterPaginator(
            object_list=queryset,
            per_page=page_size,
            current_page=page
        )
        objs = paginator.current_page
        return (paginator, page, objs, True)

    def get_context_data(self, **kwargs):
        kwargs['all'] = True
        return super(MatchListView, self).get_context_data(**kwargs)


class ParsedMatchListView(MatchListView):
    queryset = Match.parsed.all()
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['parsed'] = True
        return super(ParsedMatchListView, self).get_context_data(**kwargs)
