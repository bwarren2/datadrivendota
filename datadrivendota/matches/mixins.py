from .models import PlayerMatchSummary


class RecentPmsesMixin(object):

    def get_context_data(self, **kwargs):

        if self.request.user.is_authenticated():

            kwargs['recent_pmses'] = PlayerMatchSummary.parsed.filter(
                player__steam_id=self.request.user.userprofile.steam_id
            ).select_related().order_by('player_slot')[:12]

        return super(RecentPmsesMixin, self).get_context_data(**kwargs)
