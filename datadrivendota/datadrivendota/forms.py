from django import forms


class KeyForm(forms.Form):
    code = forms.CharField()
