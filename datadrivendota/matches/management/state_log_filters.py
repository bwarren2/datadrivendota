# Things that come from entity states
# player_slot
# tick_time
# hero_id


def damage(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'base_damage': (msg['damage_max'] + msg['damage_min'])/2,
                'bonus_damage': msg['damage_bonus'],
                'total_damage': (msg['damage_max'] + msg['damage_min'])/2 +
                msg['damage_bonus']
            }
            for msg in msgs
            if 'damage_max' in msg and
            'damage_min' in msg and
            'damage_bonus' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def health(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'health': msg['health'],
                'max_health': msg['max_health']
            }
            for msg in msgs
            if 'health' in msg and
            'max_health' in msg and
            msg['hero_id'] == pms.hero.steam_id

        ],
        key=lambda x: x['offset_time']
    )


def mana(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'mana': msg['mana'],
                'max_mana': msg['max_mana']
            }
            for msg in msgs
            if 'mana' in msg and
            'max_mana' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def items(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'item_0': msg['item_0'],
                'item_1': msg['item_1'],
                'item_2': msg['item_2'],
                'item_3': msg['item_3'],
                'item_4': msg['item_4'],
                'item_5': msg['item_5'],
            }
            for msg in msgs
            if msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def position(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'x': msg['x'],
                'y': msg['y'],
            }
            for msg in msgs
            if 'x' in msg and
            'y' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def agility(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'agility': msg['agility']
            }
            for msg in msgs
            if 'agility' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def agility_total(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'agility_total': msg['agility_total']
            }
            for msg in msgs
            if 'agility_total' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def strength(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'strength': msg['strength']
            }
            for msg in msgs
            if 'strength' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def strength_total(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'strength_total': msg['strength_total']
            }
            for msg in msgs
            if 'strength_total' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def intelligence(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'intelligence': msg['intelligence']
            }
            for msg in msgs
            if 'intelligence' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def intelligence_total(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'intelligence_total': msg['intelligence_total']
            }
            for msg in msgs
            if 'intelligence_total' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def damage_taken(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'damage_taken': msg['damage_taken']
            }
            for msg in msgs
            if 'damage_taken' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def healing(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'healing': msg['healing']
            }
            for msg in msgs
            if 'healing' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def kills(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'kills': msg['kills']
            }
            for msg in msgs
            if 'kills' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def deaths(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'deaths': msg['deaths']
            }
            for msg in msgs
            if 'deaths' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def assists(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'assists': msg['assists']
            }
            for msg in msgs
            if 'assists' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def last_hits(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'last_hits': msg['last_hits']
            }
            for msg in msgs
            if 'last_hits' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def denies(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'denies': msg['denies']
            }
            for msg in msgs
            if 'denies' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def misses(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'misses': msg['misses']
            }
            for msg in msgs
            if 'misses' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def lifestate(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'lifestate': msg['lifestate']
            }
            for msg in msgs
            if 'lifestate' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def magic_resist_pct(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'magic_resist_pct': msg['magic_resist_pct']
            }
            for msg in msgs
            if 'magic_resist_pct' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def armor(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'armor': msg['armor']
            }
            for msg in msgs
            if 'armor' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def recent_damage(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'recent_damage': msg['recent_damage']
            }
            for msg in msgs
            if 'recent_damage' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def respawn_time(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'respawn_time': msg['respawn_time']
            }
            for msg in msgs
            if 'respawn_time' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def roshan_kills(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'roshan_kills': msg['roshan_kills']
            }
            for msg in msgs
            if 'roshan_kills' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def nearby_creep_deaths(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'nearby_creep_deaths': msg['nearby_creep_deaths']
            }
            for msg in msgs
            if 'nearby_creep_deaths' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def shared_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'shared_gold': msg['shared_gold']
            }
            for msg in msgs
            if 'shared_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def reliable_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'reliable_gold': msg['reliable_gold']
            }
            for msg in msgs
            if 'reliable_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def total_earned_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'total_earned_gold': msg['total_earned_gold']
            }
            for msg in msgs
            if 'total_earned_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def unreliable_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'unreliable_gold': msg['unreliable_gold']
            }
            for msg in msgs
            if 'unreliable_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def creep_kill_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'creep_kill_gold': msg['creep_kill_gold']
            }
            for msg in msgs
            if 'creep_kill_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def hero_kill_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'hero_kill_gold': msg['hero_kill_gold']
            }
            for msg in msgs
            if 'hero_kill_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def income_gold(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'income_gold': msg['income_gold']
            }
            for msg in msgs
            if 'income_gold' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def tower_kills(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'tower_kills': msg['tower_kills']
            }
            for msg in msgs
            if 'tower_kills' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )


def xp(msgs, pms):
    return sorted(
        [
            {
                'offset_time': msg['offset_time'],
                'xp': msg['xp']
            }
            for msg in msgs
            if 'xp' in msg and
            msg['hero_id'] == pms.hero.steam_id
        ],
        key=lambda x: x['offset_time']
    )

entitystate_filter_map = {
    'agility': agility,
    'agility_total': agility_total,
    'strength': strength,
    'strength_total': strength_total,
    'intelligence': intelligence,
    'intelligence_total': intelligence_total,
    'damage': damage,
    'damage_taken': damage_taken,
    'healing': healing,
    'health': health,
    'mana': mana,
    'kills': kills,
    'deaths': deaths,
    'assists': assists,
    'items': items,
    'last_hits': last_hits,
    'denies': denies,
    'misses': misses,
    'lifestate': lifestate,
    'magic_resist_pct': magic_resist_pct,
    'armor': armor,
    'recent_damage': recent_damage,
    'respawn_time': respawn_time,
    'roshan_kills': roshan_kills,
    'nearby_creep_deaths': nearby_creep_deaths,
    'shared_gold': shared_gold,
    'reliable_gold': reliable_gold,
    'total_earned_gold': total_earned_gold,
    'unreliable_gold': unreliable_gold,
    'creep_kill_gold': creep_kill_gold,
    'hero_kill_gold': hero_kill_gold,
    'income_gold': income_gold,
    'tower_kills': tower_kills,
    'xp': xp,
    'position': position,
}
