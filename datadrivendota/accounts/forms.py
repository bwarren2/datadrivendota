from django import forms


class PollForm(forms.Form):
    CHOICES = [
        (item, item.replace("_", " ").title())
        for item in ['no', 'yes']
    ]
    premium = forms.ChoiceField(
        label="Would you pay $2.49/mo for your replays to be parsed?",
        choices=CHOICES,
        widget=forms.RadioSelect
    )
    steam_id = forms.IntegerField(
        label="Your steam ID (Optional, For Prizes)",
        required=False,
        # help_text="For claiming a prize if you win one"
    )

    def clean_steam_id(self):
        if self.cleaned_data['steam_id'] is None:
            return 0
        else:
            return self.cleaned_data['steam_id']
