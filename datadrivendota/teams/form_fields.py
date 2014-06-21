from django import forms
from .models import Team
from django.core.exceptions import MultipleObjectsReturned
from urllib import unquote


class SingleTeamField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-team-tags'})

    def clean(self, team_name):
        if self.required and not team_name:
            raise forms.ValidationError("That is not a real team name")
        if not self.required and not team_name:
            return None
        if "," in team_name:
            raise forms.ValidationError(
                "Only one team please. "
                "Commas in names also trigger this error."
            )
        team_name = unquote(team_name)
        try:
            team = Team.objects.get(teamdossier__name=team_name)
        except team.DoesNotExist:
            raise forms.ValidationError("I do not have a team by that name")
        except MultipleObjectsReturned:
            raise forms.ValidationError(
                "I could not uniquely identify that team"
            )
        return team.steam_id

