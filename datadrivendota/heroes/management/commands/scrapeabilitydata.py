from django.core.management.base import BaseCommand
from uuid import uuid4
from django.utils.text import slugify
from django.core.files import File
from BeautifulSoup import BeautifulSoup

from json import loads
from urllib2 import urlopen, HTTPError
from heroes.models import (
    Ability,
    AbilitySpecialValues,
    AbilityBehavior,
    AbilityUnitTargetFlags,
    AbilityUnitTargetType,
    AbilityUnitTargetTeam,
    Hero
)


class Command(BaseCommand):

    def handle(self, *args, **options):

        url = 'http://www.dota2.com/jsfeed/abilitydata'
        ability_text = loads(urlopen(url).read())['abilitydata']

        with open('json_files/npc_abilities.json') as f:
            abilities = loads(f.read())['DOTAAbilities']
        del abilities['Version']  # Purge a junk field

        mapping_dict = {
            'AbilityDuration': 'duration',
            'AbilityChannelTime': 'channel_time',
            'AbilityDamage': 'damage',
            'AbilityUnitDamageType': 'damage_type',
            'AbilityCastRange': 'cast_range',
            'AbilityManaCost': 'mana_cost',
            'AbilityCastPoint': 'cast_point',
            'AbilityCooldown': 'cooldown',
            'ID': 'steam_id',
        }

        #Core ability attributes
        keep_going = False
        for ability, data_dict in abilities.iteritems():
            print ability
            # if ability == 'oracle_fortunes_end':
            #     import pdb;pdb.set_trace()
            if ability == 'greevil_miniboss_orange_light_strike_array':
                keep_going = False
            if keep_going:
                continue
            ab = Ability.objects.get_or_create(
                steam_id=data_dict['ID'],
                #is_ultimate=False,
                )[0]
                #I am not sure why the is_ultimate flag is needed.  The field looks optional to me.  Ask Kit.
            for key, value in mapping_dict.iteritems():
                try:
                    trait = data_dict.get(key)
                    if trait is not None:
                        setattr(ab, value, trait)
                        ab.internal_name = ability
                    if (
                            data_dict.get('AbilityType', '')
                            == 'DOTA_ABILITY_TYPE_ULTIMATE'
                            ):
                        ab.is_ultimate = True
                except AttributeError:
                    print "Failed on {key} {value} for ability {ab}".format(
                        ab=ab,
                        key=key,
                        value=value
                    )
            try:
                ability_text_dict = ability_text[ability]
                ab.name = BeautifulSoup(
                    ability_text_dict['dname']
                ).getText(separator=u' ')
                ab.description = BeautifulSoup(
                    ability_text_dict['desc']
                ).getText(separator=u' ')
                ab.notes = BeautifulSoup(
                    ability_text_dict['notes']
                ).getText(separator=u' ')
                ab.lore = BeautifulSoup(
                    ability_text_dict['lore']
                ).getText(separator=u' ')
                # Stupid hack to deal with abilitydata js feed formatting
                # error.
                if ability_text_dict['hurl'] == 'LegionCommander':
                    ability_text_dict['hurl'] = u"Legion_Commander"
                hero_slug = slugify(
                    ability_text_dict['hurl'].replace("_", " ")
                )
                hero = Hero.objects.get(machine_name=hero_slug)
                ab.hero = hero
                ab.is_core = True
            except KeyError:
                print "Keyerror on {key} {value} for ability {ab}".format(
                    ab=ab,
                    key=key,
                    value=value
                )

            url = (
                'http://media.steampowered.com'
                '/apps/dota2/images/abilities/{ability}_hp2.png'
            ).format(ability=ability)
            try:
                imgdata = urlopen(url)
                with open('%s.png' % str(uuid4()), 'w+') as f:
                    f.write(imgdata.read())
                filename = slugify(ability)+'_full.png'
                ab.picture.save(filename, File(open(f.name)))
            except HTTPError, err:
                ab.picture = None
                print "No mugshot for %s!  Error %s" % (ability, err)

            ab.save()

            #If there are special values, map them in.
            try:
                special_dict = data_dict['AbilitySpecial']
                for idx, pairs_dict in special_dict.iteritems():
                    for key, value in pairs_dict.iteritems():
                        if key != 'var_type':
                            asv = AbilitySpecialValues.objects.get_or_create(
                                ability=ab,
                                key=key
                            )[0]
                            asv.value = value

                            asv.save()
            except KeyError:
                pass

            try:
                param_str = data_dict['AbilityUnitTargetFlags']
                for param in param_str.split("|"):
                    autf = AbilityUnitTargetFlags.objects.get_or_create(
                        internal_name=param
                    )[0]
                    autf.save()
                    ab.target_flags.add(autf)
            except KeyError:
                pass

            #The difference is an s.  I do not know why they do that.
            try:
                param_str = data_dict['AbilityUnitTargetFlag']
                for param in param_str.split("|"):
                    autf = AbilityUnitTargetFlags.objects.get_or_create(
                        internal_name=param
                    )[0]
                    autf.save()
                    ab.target_flags.add(autf)
            except KeyError:
                pass

            try:
                param_str = data_dict['AbilityBehavior']
                for param in param_str.split("|"):
                    abehav = AbilityBehavior.objects.get_or_create(
                        internal_name=param
                    )[0]
                    abehav.save()
                    ab.behavior.add(abehav)
            except KeyError:
                pass

            try:
                param_str = data_dict['AbilityUnitTargetType']
                for param in param_str.split("|"):
                    auttype = AbilityUnitTargetType.objects.get_or_create(
                        internal_name=param
                    )[0]
                    auttype.save()
                    ab.target_type.add(auttype)
            except KeyError:
                pass

            try:
                param_str = data_dict['AbilityUnitTargetTeam']
                for param in param_str.split("|"):
                    autteam = AbilityUnitTargetTeam.objects.get_or_create(
                        internal_name=param
                    )[0]
                    autteam.save()
                    ab.target_team.add(autteam)
            except KeyError:
                pass
