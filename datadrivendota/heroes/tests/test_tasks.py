from django.test import TestCase
from datadrivendota.management.tasks import ApiContext
from heroes.management.tasks import MirrorHeroSkillData


# class TestHeroSkillData(TestCase):

#     def setUp(self):
#         self.task = MirrorHeroSkillData()

#     def test_empty_validator(self):
#         c = ApiContext()
#         self.task.api_context = c
#         self.assertEqual(self.task.valid_context(), False)

#     def test_bad_validator(self):
#         c = ApiContext()
#         c.account_id = 2
#         self.task.api_context = c
#         self.assertEqual(self.task.valid_context(), False)

#     def test_good_validator(self):
#         c = ApiContext()
#         c.hero_id = 1
#         c.account_id = None
#         self.task.api_context = c
#         self.assertEqual(self.task.valid_context(), True)

#     def test_context_filling(self):
#         c = ApiContext()
#         c.hero_id = 1
#         c.account_id = None

#         self.task.api_context = c
#         self.task.fill_default_context()
#         self.assertEqual(self.task.api_context.matches_requested, 100)
#         self.assertEqual(self.task.api_context.matches_desired, 100)
#         self.assertEqual(self.task.api_context.skill_levels, [1, 2, 3])

#         self.task.api_context = c
#         c.matches_requested = 10
#         c.matches_desired = 20
#         c.skill_levels = 10
#         self.task.fill_default_context()
#         self.assertEqual(self.task.api_context.matches_requested, 10)
#         self.assertEqual(self.task.api_context.matches_desired, 20)
#         self.assertEqual(self.task.api_context.skill_levels, [1, 2, 3])
