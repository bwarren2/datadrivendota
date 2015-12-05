from django.views.generic import DetailView, ListView, TemplateView
from utils.views import ability_infodict

from .models import Match, PlayerMatchSummary, PickBan
from utils.pagination import SmarterPaginator


class MatchDetail(DetailView):
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'


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


class ReplicateDetail(DetailView):
    template_name = 'matches/replicate.html'
    model = Match
    slug_url_kwarg = 'match_id'
    slug_field = 'steam_id'


class TimeLapseDetail(TemplateView):
    template_name = 'matches/time_lapse.html'


class MatchListView(ListView):
    model = Match
    paginate_by = 10

    def get_queryset(self):
        filter_league = self.request.GET.get('league_id', None)

        if filter_league:
            matches = Match.objects.filter(
                league__steam_id=filter_league,
                validity=Match.LEGIT
            )
        else:
            matches = Match.objects.filter(
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
    kwargs['match'] = self.object
    summaries = PlayerMatchSummary.objects.filter(
        match=self.object
    ).select_related().order_by('player_slot')

    kwargs['summaries'] = summaries

    radiant_summaries = [
        summary for summary in summaries if summary.side == 'Radiant'
    ]
    radiant_infodict = {}
    min_skill_length = 10
    for summary in radiant_summaries:
        radiant_infodict[summary.player_slot] = ability_infodict(summary)
        min_skill_length = min(
            min_skill_length,
            len(radiant_infodict[summary.player_slot]['ability_dict'])
        )
    kwargs['radiant_infodict'] = radiant_infodict

    dire_summaries = [
        summary for summary in summaries if summary.side == 'Dire'
    ]
    dire_infodict = {}
    for summary in dire_summaries:
        dire_infodict[summary.player_slot] = ability_infodict(summary)
    kwargs['dire_infodict'] = dire_infodict

    kwargs['min_skill_length'] = min_skill_length

    # Identify any pickbans for templating.
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
        return super(MatchDetail, self).get_context_data(**kwargs)
