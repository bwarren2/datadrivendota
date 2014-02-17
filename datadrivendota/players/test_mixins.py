from matches.models import PlayerMatchSummary


class PlayerValidityMixin(object):
    def setUp(self):
        self.valid_player = PlayerMatchSummary.objects.all()[0].player.steam_id
        self.invalid_player = -1
        self.valid_player_list = [
            pms.player.steam_id
            for pms in PlayerMatchSummary.objects.all()[0:3]
        ]
        self.invalid_player_list = []
        super(PlayerValidityMixin, self).setUp()
