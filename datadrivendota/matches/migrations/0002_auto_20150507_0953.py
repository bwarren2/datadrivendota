# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


def add_modes(apps, schema_editor):
    GameMode = apps.get_model('matches', 'GameMode')
    modes = {
        0:
            {'is_competitive': False, 'description': 'None', 'visible': False},
        1:
            {
                'is_competitive': True,
                'description': 'All Pick',
                'visible': True
            },
        2:
            {'is_competitive': True,
                'description': "Captain's Mode", 'visible': True},
        3:
            {'is_competitive': True,
                'description': 'Random Draft', 'visible': True},
        4:
            {'is_competitive': True,
                'description': 'Single Draft', 'visible': True},
        5:
            {'is_competitive': True,
                'description': 'All Random', 'visible': True},
        6:
            {'is_competitive': False,
                'description': 'Intro', 'visible': False},
        7:
            {'is_competitive': False,
                'description': 'Diretide', 'visible': True},
        8:
            {
                'is_competitive': False,
                'description': "Reverse Captain's",
                'visible': True
            },
        9:
            {'is_competitive': False,
                'description': 'Christmas', 'visible': False},
        10:
            {
                'is_competitive': False,
                'description': 'Tutorial', 'visible': False
            },
        11:
            {
                'is_competitive': False,
                'description': 'Mid Only',
                'visible': True
            },
        12:
            {
                'is_competitive': False,
                'description': 'Least Played',
                'visible': True
            },
        13:
            {
                'is_competitive': False,
                'description': 'New Player Pool',
                'visible': True
            },
        14:
            {
                'is_competitive': False,
                'description': 'Compendium Matchmaking',
                'visible': True
            },
        15:
            {
                'is_competitive': False,
                'description': 'Custom',
                'visible': True
            },
        16:
            {
                'is_competitive': True,
                'description': "Captain's Draft",
                'visible': True
            },
        17:
            {
                'is_competitive': False,
                'description': 'Balanced Draft',
                'visible': True
            },
        18:
            {
                'is_competitive': False,
                'description': 'Ability Draft',
                'visible': True,
            },
        19:
            {'is_competitive': False, 'description': 'Event', 'visible': True},
        20:
            {
                'is_competitive': False,
                'description': 'All Random Deathmatch',
                'visible': True
            },
        21:
            {
                'is_competitive': False,
                'description': 'Solo Mid',
                'visible': True
            },
        22:
            {
                'is_competitive': False,
                'description': 'All Draft',
                'visible': True
            }
    }
    for id, infodict in modes.items():
        GameMode.objects.update_or_create(steam_id=id, defaults=infodict)


def add_leavers(apps, schema_editor):
    LeaverStatus = apps.get_model('matches', 'LeaverStatus')
    dct = {
        0: 'None',
        1: 'Disconnected',
        2: 'Disconnected, Too Long',
        3: 'Abandoned',
        4: 'AFK',
        5: 'Never Connected',
        6: 'Never Connected, Too Long',
        7: 'Failed to Ready Up',
        8: 'Declined'
    }
    for id, desc in dct.iteritems():
        LeaverStatus.objects.update_or_create(
            steam_id=id,
            defaults={'description': desc}
        )


def add_lobbies(apps, schema_editor):
    LobbyType = apps.get_model('matches', 'LobbyType')

    dct = {
        -1: 'Invalid',
        0: 'Casual match',
        1: 'Practice',
        2: 'Tournament',
        4: 'Coop with Bots',
        5: 'Legacy Team Match',
        6: 'Legacy Solo Queue',
        7: 'Competitive Match',
        8: 'Casual1v1 Match',
        9: 'Weekend Tourney',
        10: 'Local Bot Match'
    }
    for id, desc in dct.iteritems():
        LobbyType.objects.update_or_create(
            steam_id=id,
            defaults={'description': desc}
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_modes, noop),
        migrations.RunPython(add_leavers, noop),
        migrations.RunPython(add_lobbies, noop),
    ]
