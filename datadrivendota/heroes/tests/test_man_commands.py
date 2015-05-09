from django.test import TestCase
from heroes.models import Hero
from heroes.management.commands import scrapeabilitydata as ability_task
from heroes.management.commands.scrapeheroes import Command as hero_task
from .json_samples import (
    ability_numbers,
    ability_text,
    ability_merge,
    heroes,
    )


class TestAbilityImport(TestCase):

    def test_dict_merge(self):
        lore_dict = ability_text
        number_dict = ability_numbers
        output = ability_task.assemble_data(lore_dict, number_dict)
        self.assertEqual(output, ability_merge)


class TestHeroImport(TestCase):

    @classmethod
    def setUpClass(self):
        super(self, TestHeroImport).setUpClass()     # Call parent first
        self.json_data = heroes
        self.command = hero_task
        Hero.objects.all().delete()

    @classmethod
    def tearDownClass(self):
        Hero.objects.all().delete()
        super(self, TestHeroImport).tearDownClass()  # Call parent last

    def test_hero_create(self):
        hero_task().create_heroes(self.json_data)
        self.assertEqual(110, Hero.objects.all().count())
        self.assertEqual(0, Hero.objects.filter(internal_name='').count())
        self.assertEqual(0, Hero.objects.filter(name='').count())
        self.assertEqual(0, Hero.objects.filter(steam_id__lte=0).count())
        self.assertEqual(0, Hero.objects.filter(steam_id__gte=113).count())
