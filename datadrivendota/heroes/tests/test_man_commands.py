from django.test import TestCase
from heroes.management.commands import scrapeabilitydata as ability_task
from .json_samples import ability_numbers, ability_text, ability_merge


class TestAbilityImport(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_dict_merge(self):
        lore_dict = ability_text
        number_dict = ability_numbers
        output = ability_task.assemble_data(lore_dict, number_dict)
        self.assertEqual(output, ability_merge)
