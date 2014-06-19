from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Team


class TeamList(ListView):
    """The index of imported leagues"""
    model = Team

    def get_queryset(self):
        qs = self.model.objects.all().select_related()
        return qs
