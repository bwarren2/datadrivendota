from optparse import make_option
from json import dumps, loads
from BeautifulSoup import BeautifulSoup
from urllib2 import urlopen, HTTPError
import re
import csv

from django.core.management.base import BaseCommand

from heroes.models import Hero, HeroDossier
from heroes.models import HeroDossier, Hero, Role, Assignment


class Command(BaseCommand):

    option_list = BaseCommand.option_list+(
        make_option('--file',
                    action='store',
                    dest='source_file',
                    help='What file should I open?',),
    )

    def handle(self, *args, **options):
        # @todo: This whole method should be decomposed into well-named
        # smaller methods. Try to keep linecount under a dozen.
        # --kit 2014-02-16

        with open('json_files/npc_heroes.json') as f:
            stats = loads(f.read())['DOTAHeroes']
        try:
            del stats['Version']  # Purge a junk field
        except KeyError:
            # Probably manually deleted.
            pass
        mapping_dict = {
            "MovementSpeed": "movespeed",
            "StatusHealthRegen": "hp_regen",
            "StatusManaRegen": "mana_regen",
            "AttackRange": "range",
            "AttributeBaseStrength": "strength",
            "AttributeBaseAgility": "agility",
            "AttributeBaseIntelligence": "intelligence",
            "AttributeStrengthGain": "strength_gain",
            "AttributeAgilityGain": "agility_gain",
            "AttributeIntelligenceGain": "intelligence_gain",
            "AttackRate": "base_atk_time",
            "VisionDaytimeRange": "day_vision",
            "VisionNighttimeRange": "night_vision",
            "AttackAnimationPoint": "atk_point",
            "MovementTurnRate": "turn_rate",
        }

        alignment_dict = {
            "DOTA_ATTRIBUTE_INTELLECT": HeroDossier.INTELLIGENCE,
            "DOTA_ATTRIBUTE_AGILITY": HeroDossier.AGILITY,
            "DOTA_ATTRIBUTE_STRENGTH": HeroDossier.STRENGTH
        }

        attr_dict = {
            "DOTA_ATTRIBUTE_STRENGTH": "AttributeBaseStrength",
            "DOTA_ATTRIBUTE_AGILITY": "AttributeBaseAgility",
            "DOTA_ATTRIBUTE_INTELLECT": "AttributeBaseIntelligence"
        }

        # Core ability attributes
        for machine_name, data_dict in stats.iteritems():
            # @todo: Probably don't use a magic string here. Possibly set some
            # per- app cosntants for values consumed from Valve API?
            # --kit 2014-02-16
            if machine_name != 'npc_dota_hero_base':
                print machine_name, data_dict['HeroID']
                try:
                    hero = Hero.objects.get(
                        steam_id=data_dict['HeroID']
                        )
                except Hero.DoesNotExist:
                    hero = Hero.objects.create(
                        steam_id=data_dict['HeroID'],
                        machine_name=machine_name,
                        name=machine_name[len('npc_dota_hero_'):].replace(
                            "_", " ").title(),
                        )

                default_dict = {}
                for valve_name, my_name in mapping_dict.iteritems():
                    trait = data_dict.get(
                        valve_name,
                        stats['npc_dota_hero_base'][valve_name]
                    )
                    if trait is not None:
                        default_dict[my_name] = trait

                default_dict['armor'] = (
                    (float(default_dict['agility']) / 7.0)
                    + float(data_dict.get(
                        'ArmorPhysical',
                        stats['npc_dota_hero_base']['ArmorPhysical']
                    ))
                )
                default_dict['hp'] = 150 + 19 * int(default_dict['strength'])
                default_dict['alignment'] = alignment_dict[
                    data_dict['AttributePrimary']
                ]
                default_dict['mana'] = float(default_dict['intelligence']) * 13
                # @todo: Please don't use postposed conditionals; bad Python
                # style.
                # --kit 2014-02-16
                default_dict['projectile_speed'] = data_dict.get(
                    "ProjectileSpeed",
                    0
                ) if data_dict.get("ProjectileSpeed", 0) != '' else 0

                # Valve does not count the dmg gain from primary stat in their
                # base assessment
                default_dict['min_dmg'] = data_dict.get(
                    "AttackDamageMin",
                    stats['npc_dota_hero_base'][valve_name]
                )
                default_dict['min_dmg'] = (
                    int(default_dict['min_dmg'])
                    + float(data_dict[attr_dict[data_dict[
                        'AttributePrimary'
                    ]]])
                )
                default_dict['max_dmg'] = data_dict.get(
                    "AttackDamageMax",
                    stats['npc_dota_hero_base'][valve_name]
                )
                default_dict['max_dmg'] = (
                    int(default_dict['max_dmg'])
                    + float(data_dict[attr_dict[data_dict[
                        'AttributePrimary'
                    ]]])
                )

                dos, created = HeroDossier.objects.get_or_create(
                    hero=hero,
                    defaults=default_dict
                )

                if not created:
                    for field, value in default_dict.iteritems():
                        setattr(dos, field, value)

                dos.save()

                try:
                    key = "Role"
                    role_list = data_dict.get(key).split(",")
                    key = "Rolelevels"
                    role_level_list = data_dict.get(key).split(",")
                    if role_list != ['']:
                        role_data = zip(role_list, role_level_list)
                        for role, level in role_data:
                            r = Role.objects.get_or_create(name=role)[0]
                            assignment = Assignment.objects.get_or_create(
                                hero=hero,
                                role=r,
                                magnitude=int(level))[0]
                            assignment.save()
                except AttributeError:
                    pass
                    #This means roles are not defined.  Sometimes happens with heroes in the prerelease phase/Abaddon.

        # Backswings
        # Sometimes the wiki does not purge old heroes (skeleton king)
        try:
            print "Trying animations.  You remembered to format it correctly, right?."
            with open('animations.csv', 'r') as f:

                reader = csv.reader(
                    f, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL
                    )
                reader.next()
                for row in reader:
                    try:
                        doss = HeroDossier.objects.get(hero__name=row[0])
                        doss.atk_point = row[1]
                        doss.atk_backswing = row[2]
                        doss.cast_point = row[3]
                        doss.cast_backswing = row[4]
                        doss.save()
                    except Hero.DoesNotExist:
                        print row
                        print "FREAK OUT"
        except Exception as err:
            print err.strerror
            print "Animations not imported."
