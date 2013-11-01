from .models import Match

class MatchValidityMixin(object):
    def setUp(self):
        self.valid_x_var = 'duration'
        self.invalid_x_var = 'blicketude'
        self.valid_y_var='kills'
        self.invalid_y_var='snufflupagus'
        self.valid_cat_var='is_win'
        self.invalid_cat_var='chumbliness'
        self.valid_game_modes=[1,2,3]
        self.invalid_game_modes=[-1,-2]
        self.valid_match = Match.objects.all()[0].steam_id
        self.invalid_match = -1
        super(MatchValidityMixin,self).setUp()
