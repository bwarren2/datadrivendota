from django import forms
from matches.models import GameMode



game_modes = GameMode.objects.all()
game_mode_choices = [(gm.steam_id, gm.description) for gm in game_modes]

game_modes = GameMode.objects.filter(is_competitive=True)
game_mode_defaults = [gm.steam_id for gm in game_modes]

class MultiGameModeSelect(forms.MultipleChoiceField):

    choices=game_mode_choices
    initial=game_mode_defaults
