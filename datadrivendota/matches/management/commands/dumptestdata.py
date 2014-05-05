from django.core.management.base import BaseCommand
from django.core import serializers
from matches.models import (
    PlayerMatchSummary,
    SkillBuild,
    GameMode,
    LeaverStatus,
    LobbyType,
    )
from heroes.models import Hero, HeroDossier, Role, Assignment
from items.models import Item, ItemAttributes, ItemComponents
"""Currently, the various Ability helper models are unsupported, as are UserProfiles"""


class Command(BaseCommand):

    def handle(self, *app_labels, **options):
        """
        This function acquires a set of objects to fill in test data, but limits fixture size by only taking a small number of objects and only guaranteeing full coverage (all skill levels) for one hero.  By convention, that hero is Juggernaut.

        For players tests, we need at least two players, some of which are pros.  By convention, those players are s4 and Dendi."""
        num_matches = 4
        testing_hero = Hero.objects.get(name='Juggernaut')  # Juggernaut
        pms_list = []
        for skill in range(0, 5):
            skill_sample_matches = PlayerMatchSummary.objects.filter(
                match__skill=skill, hero=testing_hero
                ).order_by('-match__start_time')[0:num_matches]
            pms_list.extend(skill_sample_matches)

        cms = PlayerMatchSummary.objects.filter(
            hero=testing_hero, match__game_mode__description="Captains Mode"
        ).order_by('-match__start_time')[0:num_matches]
        pms_list.extend([c for c in cms])

        #Dendi
        dendiboss = PlayerMatchSummary.objects.filter(
            player__steam_id=70388657
        ).order_by('-match__start_time')[0:num_matches]
        pms_list.extend([c for c in dendiboss])

        #Dendi
        s4 = PlayerMatchSummary.objects.filter(
            player__steam_id=41231571
        ).order_by('-match__start_time')[0:num_matches]
        pms_list.extend([c for c in s4])


        sample_matches = [s.match for s in pms_list]
        pms = PlayerMatchSummary.objects.filter(match__in=sample_matches)
        players = [summary.player for summary in pms]
        heroes = [hero for hero in Hero.objects.all()]
        dossiers = [d for d in HeroDossier.objects.all()]
        pickbans = [
            pb
            for match in sample_matches
            for pb in match.pickban_set.all()]
        builds = SkillBuild.objects.filter(player_match_summary__in=pms)
        abilities = [build.ability for build in builds]
        dossier = HeroDossier.objects.get(hero=testing_hero)
        roles = Role.objects.filter(hero=testing_hero)
        assignments = Assignment.objects.filter(hero=testing_hero)
        game_modes = GameMode.objects.all()
        lobby_types = LobbyType.objects.all()
        leaver_statuses = LeaverStatus.objects.all()
        items = Item.objects.all()
        items_attrs = ItemAttributes.objects.all()
        items_components = ItemComponents.objects.all()

        serializing_list = []

        for player in players:
            serializing_list.append(player)

        for hero in heroes:
            serializing_list.append(hero)

        for d in dossiers:
            serializing_list.append(d)

        for match in sample_matches:
            serializing_list.append(match)

        for summary in pms:
            serializing_list.append(summary)

        for build in builds:
            serializing_list.append(build)

        for ability in abilities:
            serializing_list.append(ability)

        for role in roles:
            serializing_list.append(role)

        for assignment in assignments:
            serializing_list.append(assignment)

        for item in game_modes:
            serializing_list.append(item)

        for item in lobby_types:
            serializing_list.append(item)

        for item in leaver_statuses:
            serializing_list.append(item)

        for item in items:
            serializing_list.append(item)

        for item in items_attrs:
            serializing_list.append(item)

        for item in items_components:
            serializing_list.append(item)

        for pb in pickbans:
            serializing_list.append(item)


        self.stdout.ending = None
        serializers.serialize('json', serializing_list, stream=self.stdout)
