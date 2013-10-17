from django import forms
from .models import Player


class SinglePlayerField(forms.CharField):
    widget=forms.TextInput(attrs={'class':'playertags'})

    def clean(self, player):
        player_name = player
        if player_name is None or player_name == '':
            raise forms.ValidationError("That is not a real player name")
        if "," in player_name:
            raise forms.ValidationError("Only one player please.  Commas in names also trigger this error.")
        try:
            player = Player.objects.get(persona_name=player_name)
        except Player.DoesNotExist:
            raise forms.ValidationError("I do not have a player by that name")
        return player.steam_id

