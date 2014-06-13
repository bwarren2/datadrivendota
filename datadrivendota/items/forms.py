from django import forms
from players.form_fields import SinglePlayerField
from heroes.form_fields import SingleHeroSelect
from matches.form_fields import MultiGameModeSelect


class ItemWinrateForm(forms.Form):
    SKILL_LEVELS = [
        (1, 'Normal Skill'),
        (2, 'High Skill'),
        (3, 'Very High Skill'),
    ]

    player = SinglePlayerField(
        required=False,
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
    skill_level = forms.ChoiceField(
        choices=SKILL_LEVELS,
        required=False,
        help_text='What goes on the Y axis?'
    )

