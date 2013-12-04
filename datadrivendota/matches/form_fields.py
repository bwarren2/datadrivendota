from django import forms
from .models import GameMode

__all__ = (
    'MultiGameModeSelect',
)


GAME_MODES = GameMode.objects.filter(visible=True)
GAME_MODE_CHOICES = [(gm.steam_id, gm.description) for gm in GAME_MODES]

GAME_MODES = GameMode.objects.filter(is_competitive=True, visible=True)
GAME_MODE_DEFAULTS = [gm.steam_id for gm in GAME_MODES]


class MultiGameModeSelect(forms.MultipleChoiceField):
    widget = forms.SelectMultiple(attrs={'class': 'multi-game-mode'})

    def __init__(self, *args, **kwargs):
        super(MultiGameModeSelect, self).__init__(*args, **kwargs)
        self.choices = GAME_MODE_CHOICES
        self.initial = GAME_MODE_DEFAULTS
