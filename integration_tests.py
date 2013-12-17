from splinter import Browser
from django.test import LiveServerTestCase

from heroes.models import Hero


class BaseIntegrationTest(LiveServerTestCase):
    implicit_wait = 3

    @classmethod
    def setUpClass(cls):
        cls.browser = Browser(driver_name='phantomjs')
        super(BaseIntegrationTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.browser.quit()
        super(BaseIntegrationTest, cls).tearDownClass()

    def get(self, path, query=None):
        return self.browser.visit("{scheme_host_port}{path}".format(
            scheme_host_port=self.live_server_url,
            path=path
        ))

    def css(self, selector):
        return self.browser.find_elements_by_css_selector(selector)

    def css_count(self, selector):
        return len(self.css(selector))

    def css_single(self, selector):
        return self.css(selector)[0]


class IntegrationTest(BaseIntegrationTest):
    def test_title(self):
        self.get('/')
        self.assertIn('datadrivendota', self.browser.title)


class HeroesIntegrationTest(BaseIntegrationTest):
    pass
    # def test_index(self):
    #     self.get('/heroes/')
    #     for hero in Hero.objects.all():
    #         self.assertEqual(
    #             self.css_count("a[href={link}]".format(
    #                 link=hero.get_absolute_url()
    #             )),
    #             1
    #         )

    # def test_vitals_get(self):
    #     self.get('/heroes/vitals/')
    #     self.assertEqual(self.css_count("#id_heroes"), 1)
    #     self.assertEqual(self.css_count("input[name=stats]"), 7)
    #     self.assertEqual(self.css_count("input[name=unlinked_scales]"), 1)

    # def test_vitals_post(self):
    #     self.get('/heroes/vitals/')
    #     # The following form entry fails because the database is not
    #     # initialized correctly.
    #     self.css_single('#id_heroes').send_keys("Faceless Void")
    #     self.css_single('#id_stats_3').click()
    #     self.css_single('#id_stats_5').click()
    #     self.css_single('button[type=submit]').click()
    #     self.assertEqual(self.css_count('.error'), 0)

    # def test_vitals_post_bad(self):
    #     self.get('/heroes/vitals/')
    #     # The following form entry fails because the database is not
    #     # initialized correctly.
    #     self.css_single('#id_heroes').send_keys("This hero doesn't exist")
    #     self.css_single('#id_stats_3').click()
    #     self.css_single('#id_stats_5').click()
    #     self.css_single('button[type=submit]').click()
    #     self.assertEqual(self.css_count('.error'), 1)

# Heroes
#  (Possibly slow-ajax-images on some pages, check)
#  Vitals
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Lineups
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Performance
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Skillbars
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)

# Items
#  Index
#  Instance

# Matches
#  Index
#  Instance (test for ajax-grabbed slow image)

# Players
#  Detail
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Winrate
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Timeline
#   Get form
#   Submit form (check for image)
#   Submit bad form (check for errors)
#  Matches
#   Generates a table
