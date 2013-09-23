from django import forms
import datetime
from matches.models import GameMode
thirty_days_ago = datetime.date.today() - datetime.timedelta(days=30)

game_modes = GameMode.objects.all()
game_mode_choices = [(gm.steam_id, gm.description) for gm in game_modes]

class PlayerWinrateLevers(forms.Form):
    player = forms.CharField(required=True)
    player.widget=forms.TextInput(attrs={'class':'playertags'})
    min_date = forms.DateField(required=False, initial=thirty_days_ago)
    min_date.widget=forms.TextInput(attrs={'class':'datepicker'})
    max_date = forms.DateField(required=False, initial=datetime.date.today)
    max_date.widget=forms.TextInput(attrs={'class':'datepicker'})
    game_modes = forms.MultipleChoiceField(choices=game_mode_choices, required=True)

