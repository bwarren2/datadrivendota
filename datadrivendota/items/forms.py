from django import forms
from players.form_fields import SinglePlayerField
from heroes.form_fields import SingleHeroSelect
from matches.form_fields import MultiGameModeSelect


class ItemWinrateForm(forms.Form):

    player = SinglePlayerField(
        required=True,
        help_text='Pick one player.  Use the autocomplete.'
    )
    hero = SingleHeroSelect(
        required=True,
        help_text='Pick one hero.  Use the autocomplete.'
    )
    game_modes = MultiGameModeSelect(
        required=True,
        help_text='Which game modes would you like to sample?'
    )
