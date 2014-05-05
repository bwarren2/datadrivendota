from .models import Hero


class HeroValidityMixin(object):
    def setUp(self):
        self.valid_hero_id = 8
        self.invalid_hero_id = 800
        self.valid_hero_name = 'Juggernaut'
        self.invalid_hero_id = 'Becky the Kite Flyer'
        self.invalid_stat = 'effervescence'
        self.valid_stat = 'strength'
        self.valid_level = 6
        self.invalid_level = -1
        self.valid_level_set = [6, 11]
        self.invalid_level_set = [-1, -2]
        self.test_hero = Hero.objects.get(steam_id=self.valid_hero)
        super(HeroValidityMixin, self).setUp()
