from django import forms
from .models import GameMode, Match
from django.forms import ValidationError

__all__ = (
    'MultiGameModeSelect',
)


class MultiGameModeSelect(forms.MultipleChoiceField):
    widget = forms.SelectMultiple(attrs={'class': 'multi-game-mode'})

    def setup(self):
        GAME_MODES = GameMode.objects.filter(visible=True)
        GAME_MODE_CHOICES = [
            (gm.steam_id, gm.description) for gm in GAME_MODES
        ]

        GAME_MODES = GameMode.objects.filter(is_competitive=True, visible=True)
        GAME_MODE_DEFAULTS = [gm.steam_id for gm in GAME_MODES]
        self.choices = GAME_MODE_CHOICES
        self.initial = GAME_MODE_DEFAULTS

    def clean(self, val):
        return [int(x) for x in val]


class MultiMatchSelect(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'multi-match-tags'})

    def clean(self, match_str):
        if match_str is None:
            return []

        match_list = match_str.split(',')
        return_match_list = []
        if match_list == ['']:
            if self.required:
                raise ValidationError("Please enter match ids")
            else:
                return []
        for match in match_list:
            try:
                found_match = Match.objects.get(steam_id=match)
            except Match.DoesNotExist:
                raise ValidationError("%s is not a valid match ID" % match)
            return_match_list.append(found_match.steam_id)

        return return_match_list


class SingleMatchSelect(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-match-tags'})

    def clean(self, match):
        if match is None:
            return []

        if ',' in match:
            raise ValidationError("Only one match at a time.")
        try:
            match = Match.objects.get(steam_id=match)
        except Match.DoesNotExist:
            raise ValidationError("We don't have that match.")

        return match.steam_id
