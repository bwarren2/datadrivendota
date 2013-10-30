from itertools import chain
from django.core.management.base import BaseCommand
from django.core import serializers
from matches.models import Match, PlayerMatchSummary, SkillBuild
from heroes.models import Hero

class Command(BaseCommand):


    def handle(self, *app_labels, **options):
        """This function acquires a set of objects to fill in test data,
        but limits fixture size by only taking a small number of objects and
        only guaranteeing full coverage (all skill levels) for one hero.
        By convention, that hero is Juggernaut."""
        num_matches=4
        testing_hero = Hero.objects.get(name='Juggernaut') # Juggernaut
        pms_list = []
        for skill in range(0,5):
            skill_sample_matches = PlayerMatchSummary.objects.filter(
                match__skill=skill, hero=testing_hero
                )[0:num_matches]
            pms_list.extend(skill_sample_matches)

        sample_matches = [s.match for s in pms_list]
        pms = PlayerMatchSummary.objects.filter(match__in=sample_matches)
        players = [summary.player for summary in pms]
        builds = SkillBuild.objects.filter(player_match_summary__in=pms)
        abilities = [build.ability for build in builds]

        serializing_list = []

        for player in players:
            serializing_list.append(player)

        for match in sample_matches:
            serializing_list.append(match)

        for summary in pms:
            serializing_list.append(summary)

        for build in builds:
            serializing_list.append(build)

        for ability in abilities:
            serializing_list.append(ability)

        self.stdout.ending = None
        serializers.serialize('json', serializing_list, stream=self.stdout)
