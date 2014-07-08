from django import forms
from .models import Player
from django.forms import ValidationError
from django.core.exceptions import MultipleObjectsReturned
from urllib import unquote


class SinglePlayerField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-player-tags'})

    def clean(self, player_id):
        if self.required and not player_id:
            raise forms.ValidationError("That is not a real player name")
        if not self.required and not player_id:
            return None
        if "," in player_id:
            raise forms.ValidationError(
                "Only one player please. "
            )
        try:
            player = Player.objects.get(steam_id=player_id)
        except Player.DoesNotExist:
            raise forms.ValidationError("I do not have a player by that name")
        except MultipleObjectsReturned:
            raise forms.ValidationError(
                "I could not uniquely identify that person"
            )
        return player.steam_id


class MultiPlayerField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'multi-player-tags'})

    def clean(self, player):
        if self.required and not player:
            raise forms.ValidationError("That is not a real player name")
        if not self.required and not player:
            return None
        player_list = player.split(',')
        return_player_list = []
        for player in player_list:
            try:
                player = Player.objects.get(steam_id=player)
            except Player.DoesNotExist:
                raise ValidationError(
                    "{player} is not a valid player name".format(player=player)
                )
            except MultipleObjectsReturned:
                raise forms.ValidationError(
                    "I could not uniquely identify {0}".format(player)
                )
            return_player_list.append(player.steam_id)
        return return_player_list


def player_by_name(player_name):
    try:
        player = Player.objects.get(pro_name=player_name)
    except Player.DoesNotExist:
        try:
            player = Player.objects.get(persona_name=player_name)
        except Player.DoesNotExist:
            raise
    return player
