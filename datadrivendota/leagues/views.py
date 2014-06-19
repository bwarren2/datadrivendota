from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import League


class LeagueList(ListView):
    """The index of imported leagues"""
    model = League

    def get_queryset(self):
        qs = self.model.objects.all().select_related()
        return qs
