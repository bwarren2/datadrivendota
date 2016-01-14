from django import forms


class MatchRequestForm(forms.Form):
    match_id = forms.IntegerField(min_value=10000, max_value=10000000000)
