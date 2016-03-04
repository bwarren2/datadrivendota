

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

    @property
    def id(self):
        # We need unique ids to avoid collisions disabling select2.
        # If you just use dataslice, frex, you cannot use two players
        # in the first slot
        return str(self.match_id)+'00000'+str(get_munged_slice(self.dataslice))

    def __repr__(self):
        return "<M#{0}, {1}>".format(self.match_id, self.dataslice)


def get_munged_slice(dataslice):
    if dataslice == 'radiant':
        return 101
    elif dataslice == 'dire':
        return 202
    elif dataslice == 'diff':
        return 303
    else:
        return dataslice
