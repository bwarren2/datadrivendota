from optparse import make_option
import json
import urllib
from django.core.management.base import BaseCommand
from heroes.models import HeroDossier, Hero


class Command(BaseCommand):

    option_list = BaseCommand.option_list+(
        make_option('--file',
                    action='store',
                    dest='source_file',
                    help='What file should I open?',),
    )

    def handle(self, *args, **options):

        """
        This function pulls either a JSON of your choosing, or the all-heroes
        data dump from jankdota and uploads those figures into the HeroDossier
        model.  NOTE: there is a hard conversion from "Wisp" to "Io" and the
        import only occurs for things in the data.  Completeness test would
        probably be good eventually.  Also, currently things overwrite on
        import; change the 'or True' below to address that.
        """
        if options['source_file'] is None:
            print("You did not specify a file; using a URL pull")
            url = "http://dotaheroes.herokuapp.com/heroes/all"
            datafile = urllib.urlretrieve(url)[0]
        else:
            datafile = open(options['source_file'])

        data = json.loads(open(datafile).read())

        for key, row in data.iteritems():
            print row
            alignment_dict = {0: 'strength', 1: 'agility', 2: 'intelligence'}

            # Yes, I know this is awful.  I am doc'ing it at the top.  It is not
            # my fault that the character had a name change and not everyone is
            # with it.
            if row['Name'] == 'Wisp':
                row['Name'] = 'Io'

            hero = Hero.objects.get(name=row['Name'])
            defaultdict = {'movespeed': row['Movespeed'],
                         'max_dmg': row['MaxDmg'],
                         'min_dmg': row['MinDmg'],
                         'hp': row['HP'],
                         'mana': row['Mana'],
                         'hp_regen': row['HPRegen'],
                         'mana_regen': row['ManaRegen'],
                         'armor': row['Armor'],
                         'range': row['Range'],
                         'projectile_speed': row['ProjectileSpeed'],
                         'strength': row['BaseStr'],
                         'agility': row['BaseAgi'],
                         'intelligence': row['BaseInt'],
                         'strength_gain': row['StrGain'],
                         'agility_gain': row['AgiGain'],
                         'intelligence_gain': row['IntGain'],
                         'alignment': alignment_dict[row['PrimaryStat']],
                         'base_atk_time': row['BaseAttackTime'],
                         'day_vision': row['DayVision'],
                         'night_vision': row['NightVision'],
                         'atk_point': row['AttackPoint'],
                         'atk_backswing':  row['AttackSwing'],
                         'cast_point': row['CastPoint'],
                         'cast_backswing': row['CastSwing'],
                         'turn_rate': row['Turnrate'],
                         'legs': row['Legs'],
            }

            dossier, created = HeroDossier.objects.get_or_create(hero=hero, defaults=defaultdict)
            if created or True:

                dossier.movespeed = row['Movespeed']
                dossier.max_dmg = row['MaxDmg']
                dossier.min_dmg = row['MinDmg']
                dossier.hp = row['HP']
                dossier.mana = row['Mana']
                dossier.hp_regen = row['HPRegen']
                dossier.mana_regen = row['ManaRegen']
                dossier.range = row['Range']
                dossier.projectile_speed = row['ProjectileSpeed']
                dossier.strength = row['BaseStr']
                dossier.agility = row['BaseAgi']
                dossier.intelligence = row['BaseInt']
                dossier.armor = row['Armor']
                dossier.strength_gain = row['StrGain']
                dossier.agility_gain = row['AgiGain']
                dossier.intelligence_gain = row['IntGain']
                dossier.alignment = alignment_dict[row['PrimaryStat']]
                dossier.base_atk_time = row['BaseAttackTime']
                dossier.day_vision = row['DayVision']
                dossier.night_vision = row['NightVision']
                dossier.atk_point = row['AttackPoint']
                dossier.atk_backswing = row['AttackSwing']
                dossier.cast_point = row['CastPoint']
                dossier.cast_backswing = row['CastSwing']
                dossier.turn_rate = row['Turnrate']
                dossier.legs = row['Legs']
            dossier.save()
