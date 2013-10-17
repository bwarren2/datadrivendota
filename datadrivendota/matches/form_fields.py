from django import forms
from matches.models import GameMode




class MultiGameModeSelect(forms.MultipleChoiceField):
    def __init__(self,*args,**kwargs):
        super(MultiGameModeSelect, self).__init__(*args, **kwargs)

        game_modes = GameMode.objects.all()
        game_mode_choices = [(gm.steam_id, gm.description) for gm in game_modes]

        game_modes = GameMode.objects.filter(is_competitive=True)
        game_mode_defaults = [gm.steam_id for gm in game_modes]

        self.choices=game_mode_choices
        self.initial=game_mode_defaults
