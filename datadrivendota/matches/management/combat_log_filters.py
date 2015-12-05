# Helpers
def targets_hero(msg):
    return msg['target_hero'] is True and msg['target_illusion'] is False


radiant_key_buildings = [
     'npc_dota_goodguys_fort',
     'npc_dota_goodguys_melee_rax_bot',
     'npc_dota_goodguys_melee_rax_mid',
     'npc_dota_goodguys_range_rax_bot',
     'npc_dota_goodguys_range_rax_mid',
     'npc_dota_goodguys_tower1_bot',
     'npc_dota_goodguys_tower1_mid',
     'npc_dota_goodguys_tower1_top',
     'npc_dota_goodguys_tower2_bot',
     'npc_dota_goodguys_tower2_mid',
     'npc_dota_goodguys_tower2_top',
     'npc_dota_goodguys_tower3_bot',
     'npc_dota_goodguys_tower3_mid',
     'npc_dota_goodguys_tower3_top',
     'npc_dota_goodguys_tower4',
]

dire_key_buildings = [
     'npc_dota_badguys_fort',
     'npc_dota_badguys_melee_rax_bot',
     'npc_dota_badguys_melee_rax_mid',
     'npc_dota_badguys_range_rax_bot',
     'npc_dota_badguys_range_rax_mid',
     'npc_dota_badguys_tower1_bot',
     'npc_dota_badguys_tower1_mid',
     'npc_dota_badguys_tower1_top',
     'npc_dota_badguys_tower2_bot',
     'npc_dota_badguys_tower2_mid',
     'npc_dota_badguys_tower2_top',
     'npc_dota_badguys_tower3_bot',
     'npc_dota_badguys_tower3_mid',
     'npc_dota_badguys_tower3_top',
     'npc_dota_badguys_tower4',
]


def kills(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'kills' and
        msg.get('attacker_source', None) == pms.hero.internal_name and
        targets_hero(msg) and
        msg.get('target', None) in enemies
    ]


def deaths(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'kills' and
        msg.get('target', None) == pms.hero.internal_name and
        targets_hero(msg) and
        msg.get('attacker_source', None) in enemies
    ]


def last_hits(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'kills' and
        msg.get('attacker_source', None) == pms.hero.internal_name and
        not targets_hero(msg) and
        msg.get('target', None) not in dire_key_buildings and
        msg.get('target', None) not in radiant_key_buildings
    ]


def xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name
    ]


def healing(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'healing' and
        msg.get('attacker_source', None) == pms.hero.internal_name and
        msg.get('target', None) in allies
    ]


def hero_dmg_taken(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('attacker_name', None) in enemies and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


def hero_dmg_dealt(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('target', None) in enemies and
        msg.get('attacker_name', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


def other_dmg_taken(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('attacker_name', None) not in enemies and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


def other_dmg_dealt(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('target', None) not in enemies and
        msg.get('target', None) not in radiant_key_buildings and
        msg.get('target', None) not in dire_key_buildings and
        msg.get('attacker_name', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


def all_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name
    ]
    pass


def earned_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) != '6'
    ]


def building_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '11'
    ]


def courier_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '15'
    ]


def creep_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '13'
    ]


def hero_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '12'
    ]


def roshan_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '14'
    ]


def buyback_expense(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '2'
    ]


def death_expense(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '1'
    ]


def hero_xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '1'
    ]


def creep_xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '2'
    ]


def roshan_xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '3'
    ]


def key_bldg_dmg_dealt(msgs, pms, enemies, allies):
    if pms.side == 'Radiant':
        return [
            msg for msg in msgs
            if msg.get('type', None) == 'damage' and
            msg.get('attacker_source', None) == pms.hero.internal_name and
            msg.get('target', None) in dire_key_buildings
        ]
    else:
        return [
            msg for msg in msgs
            if msg.get('type', None) == 'damage' and
            msg.get('attacker_source', None) == pms.hero.internal_name and
            msg.get('target', None) in radiant_key_buildings
        ]


def key_bldg_kills(msgs, pms, enemies, allies):
    if pms.side == 'Radiant':
        return [
            msg for msg in msgs
            if msg.get('type', None) == 'kills' and
            msg.get('attacker_source', None) == pms.hero.internal_name and
            msg.get('target', None) in dire_key_buildings
        ]
    else:
        return [
            msg for msg in msgs
            if msg.get('type', None) == 'kills' and
            msg.get('attacker_source', None) == pms.hero.internal_name and
            msg.get('target', None) in radiant_key_buildings
        ]


def item_buys(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'purchase' and
        msg.get('target', None) == pms.hero.internal_name
    ]


combatlog_filter_map = {
    'kills': kills,
    'deaths': deaths,
    'last_hits': last_hits,
    'xp': xp,
    'healing': healing,
    'hero_dmg_taken': hero_dmg_taken,
    'hero_dmg_dealt': hero_dmg_dealt,
    'other_dmg_taken': other_dmg_taken,
    'other_dmg_dealt': other_dmg_dealt,
    'all_income': all_income,
    'earned_income': earned_income,
    'building_income': building_income,
    'courier_kill_income': courier_kill_income,
    'creep_kill_income': creep_kill_income,
    'hero_kill_income': hero_kill_income,
    'roshan_kill_income': roshan_kill_income,
    'buyback_expense': buyback_expense,
    'death_expense': death_expense,
    'hero_xp': hero_xp,
    'creep_xp': creep_xp,
    'roshan_xp': roshan_xp,
    'key_bldg_dmg_dealt': key_bldg_dmg_dealt,
    'key_bldg_kills': key_bldg_kills,
    'item_buys': item_buys,
}
