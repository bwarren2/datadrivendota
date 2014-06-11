from django import forms


class OutcomeField(forms.ChoiceField):
    initial = 'both'
    required = False
    help_text = "Should we include matches that were won, lost, or both?"

    def __init__(self, *args, **kwargs):
        OUTCOME_CHOICES = [(item, item) for item in ['both', 'win', 'loss']]
        super(OutcomeField, self).__init__(*args, **kwargs)
        self.choices = OUTCOME_CHOICES
        self.initial = 'both'
