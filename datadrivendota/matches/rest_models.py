

class ParseShard(object):

    css_classes = None
    dataslice = None
    match_id = None
    name = None
    hero_name = None

    def __init__(
        self,
        css_classes=None,
        dataslice=None,
        match_id=None,
        name=None,
        hero_name=None
    ):
        self.css_classes = css_classes
        self.dataslice = dataslice
        self.match_id = match_id
        self.name = name
        self.hero_name = hero_name

    def merge_pms(self, pms):
        self.css_classes = pms.css_classes
        self.dataslice = pms.player_slot
        self.match_id = pms.match.steam_id
        self.name = pms.hero.name
        self.hero_name = pms.hero.internal_name

    def __repr__(self):
        return "<M#{0}, {1}>".format(self.match_id, self.dataslice)
