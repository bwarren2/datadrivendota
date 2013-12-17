from django import forms
from .models import Player
from django.forms import ValidationError
from django.core.exceptions import MultipleObjectsReturned

class SinglePlayerField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'single-player-tags'})

    def clean(self, player):
        player_name = player
        if player_name is None or player_name == '':
            raise forms.ValidationError("That is not a real player name")
        if "," in player_name:
            raise forms.ValidationError(
                "Only one player please. "
                "Commas in names also trigger this error."
            )
        try:
            player = Player.objects.get(persona_name=player_name)
        except Player.DoesNotExist:
            raise forms.ValidationError("I do not have a player by that name")
        except MultipleObjectsReturned:
            raise forms.ValidationError("I could not uniquely identify that person")
        return player.steam_id


class MultiPlayerField(forms.CharField):
    widget = forms.HiddenInput(attrs={'class': 'multi-player-tags'})

    def clean(self, player):
        player_list = player.split(',')
        return_player_list = []
        for player in player_list:
            try:
                player = Player.objects.get(persona_name=player)
            except Player.DoesNotExist:
                raise ValidationError(
                    "{player} is not a valid player name".format(player=player)
                )
            except MultipleObjectsReturned:
                raise forms.ValidationError("I could not uniquely identify {player}".format(player=player))

            return_player_list.append(player.steam_id)
        return return_player_list
