from parserpipe.decorators import mapping_construct


# Helpers
def targets_hero(msg):
    return msg['target_hero'] is True and msg['target_illusion'] is False


# Rather than explictly code a map of name to function (used in parsing),
# we decorate those functions with a dict to be modified
combatlog_filter_map = {}

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


@mapping_construct(combatlog_filter_map)
def kills(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'kills' and
        msg.get('attacker_source', None) == pms.hero.internal_name and
        targets_hero(msg) and
        msg.get('target', None) in enemies
    ]


@mapping_construct(combatlog_filter_map)
def deaths(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'kills' and
        msg.get('target', None) == pms.hero.internal_name and
        targets_hero(msg) and
        msg.get('attacker_source', None) in enemies
    ]


@mapping_construct(combatlog_filter_map)
def last_hits(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'kills' and
        msg.get('attacker_source', None) == pms.hero.internal_name and
        not targets_hero(msg) and
        msg.get('target', None) not in dire_key_buildings and
        msg.get('target', None) not in radiant_key_buildings
    ]


@mapping_construct(combatlog_filter_map)
def xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name
    ]


@mapping_construct(combatlog_filter_map)
def healing(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'healing' and
        msg.get('attacker_source', None) == pms.hero.internal_name and
        msg.get('target', None) in allies
    ]


@mapping_construct(combatlog_filter_map)
def hero_dmg_taken(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('attacker_name', None) in enemies and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


@mapping_construct(combatlog_filter_map)
def hero_dmg_dealt(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('target', None) in enemies and
        msg.get('attacker_name', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


@mapping_construct(combatlog_filter_map)
def other_dmg_taken(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'damage' and
        msg.get('attacker_name', None) not in enemies and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('target_illusion', None) is False
    ]


@mapping_construct(combatlog_filter_map)
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


@mapping_construct(combatlog_filter_map)
def all_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name
    ]
    pass


@mapping_construct(combatlog_filter_map)
def earned_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) != '6'
    ]


@mapping_construct(combatlog_filter_map)
def building_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '11'
    ]


@mapping_construct(combatlog_filter_map)
def courier_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '15'
    ]


@mapping_construct(combatlog_filter_map)
def creep_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '13'
    ]


@mapping_construct(combatlog_filter_map)
def hero_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '12'
    ]


@mapping_construct(combatlog_filter_map)
def roshan_kill_income(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '14'
    ]


@mapping_construct(combatlog_filter_map)
def buyback_expense(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '2'
    ]


@mapping_construct(combatlog_filter_map)
def death_expense(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'gold_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '1'
    ]


@mapping_construct(combatlog_filter_map)
def hero_xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '1'
    ]


@mapping_construct(combatlog_filter_map)
def creep_xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '2'
    ]


@mapping_construct(combatlog_filter_map)
def roshan_xp(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'xp_reasons' and
        msg.get('target', None) == pms.hero.internal_name and
        msg.get('key', None) == '3'
    ]


@mapping_construct(combatlog_filter_map)
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


@mapping_construct(combatlog_filter_map)
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


@mapping_construct(combatlog_filter_map)
def item_buys(msgs, pms, enemies, allies):
    return [
        msg for msg in msgs
        if msg.get('type', None) == 'purchase' and
        msg.get('target', None) == pms.hero.internal_name
    ]
