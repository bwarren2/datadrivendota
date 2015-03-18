import io
import requests
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

        lore_dict = get_text_dict()
        number_dict = get_number_dict()
        abilities = assemble_data(lore_dict, number_dict)

        # Core ability attributes
        for ability, data_dict in abilities.iteritems():

            # Make a thing.
            ab = make_ability(ability, data_dict)

            # Map in values with tricky names
            merge_mapped_values(ab, data_dict)

            # Map in text
            merge_text(ab, data_dict)

            # Get some images
            merge_image(ab, ability, data_dict)

            ab.save()

            # If there are special values, map them in.
            # This is a best-effort service; lots of passing
            merge_special_values(ab, data_dict)


def assemble_data(lore_dict, number_dict):
    for ability in number_dict.keys():
        if ability in lore_dict:
            for key, value in lore_dict[ability].iteritems():
                number_dict[ability][key] = value
    return number_dict


def get_text_dict():
    url = 'http://www.dota2.com/jsfeed/abilitydata?lang=en'
    ability_text = loads(requests.get(url).content)['abilitydata']
    return ability_text


def get_number_dict():
    with open('json_files/npc_abilities.json') as f:
        abilities = loads(f.read())['DOTAAbilities']
    del abilities['Version']  # Purge a junk field
    return abilities


def make_ability(internal_name, data_dict):
    try:
        ab = Ability.objects.get(
            steam_id=data_dict['ID'],
            )
    except Ability.DoesNotExist:
        ab = Ability.objects.create(
            steam_id=data_dict['ID'],
            internal_name=internal_name,
        )
    return ab


def merge_mapped_values(ab, data_dict):
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

    for key, value in mapping_dict.iteritems():
        try:
            trait = data_dict.get(key)
            if trait is not None:
                setattr(ab, value, trait)
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


def merge_text(ab, data_dict):
    try:
        ab.name = BeautifulSoup(
            data_dict['dname']
        ).getText(separator=u' ')
        ab.description = BeautifulSoup(
            data_dict['desc']
        ).getText(separator=u' ')
        ab.notes = BeautifulSoup(
            data_dict['notes']
        ).getText(separator=u' ')
        ab.lore = BeautifulSoup(
            data_dict['lore']
        ).getText(separator=u' ')

        hero_slug = slugify(
            data_dict['hurl'].replace("_", " ")
        )
        hero = Hero.objects.get(machine_name=hero_slug)
        ab.hero = hero
        ab.is_core = True

    except KeyError:
        print "Keyerror on text merge for ability {ab}".format(
            ab=ab,
        )


def merge_image(ab, ability, data_dict):
    url = (
        'http://media.steampowered.com'
        '/apps/dota2/images/abilities/{ability}_hp2.png'
    ).format(ability=ability)

    try:
        imgdata = requests.get(url)
        img_buffer = io.BytesIO((imgdata.content))
        filename = slugify(ability)+'_full.png'
        ab.picture.save(filename, File(img_buffer))
    except HTTPError, err:
        ab.picture = None
        print "No mugshot for %s!  Error %s" % (ability, err)


def merge_special_values(ab, data_dict):
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

    # The difference is an s.  I do not know why they do that.
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
