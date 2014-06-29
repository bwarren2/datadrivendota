from django import forms
from .models import Team
from django.core.exceptions import MultipleObjectsReturned


class SingleTeamField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-team-tags'})

    def clean(self, team_id):
        if self.required and not team_id:
            raise forms.ValidationError("That is not a real team name")
        if not self.required and not team_id:
            return None
        if "," in team_id:
            raise forms.ValidationError(
                "Only one team please. "
            )
        try:
            team = Team.objects.get(steam_id=team_id)
        except team.DoesNotExist:
            raise forms.ValidationError("I do not have a team by that name")
        except MultipleObjectsReturned:
            raise forms.ValidationError(
                "I could not uniquely identify that team"
            )
        return team.steam_id
