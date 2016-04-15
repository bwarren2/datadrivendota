from parserpipe.decorators import mapping_construct

# Things that come from entity states
# player_slot
# tick_time
# hero_id


# Rather than explictly code a map of name to function (used in parsing),
# we decorate those functions with a dict to be modified
entitystate_filter_map = {}


@mapping_construct(entitystate_filter_map)
def allstate(msgs, pms):
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
                'x': msg['x'],
                'y': msg['y'],

                'strength': msg['strength'],
                'strength_total': msg['strength_total'],
                'intelligence': msg['intelligence'],
                'intelligence_total': msg['intelligence_total'],
                'agility': msg['agility'],
                'agility_total': msg['agility_total'],

                'health': msg['health'],
                'max_health': msg['max_health'],
                'pct_health': safe_pct(msg['health'], msg['max_health']),

                'mana': msg['mana'],
                'max_mana': msg['max_mana'],
                'pct_mana': safe_pct(msg['mana'], msg['max_mana']),

                'armor': msg['armor'] + msg['agility_total'] / 7.0,

                'kills': msg['kills'],
                'deaths': msg['deaths'],
                'assists': msg['assists'],

                'last_hits': msg['last_hits'],
                'denies': msg['denies'],
                'misses': msg['misses'],
                'nearby_creep_deaths': msg['nearby_creep_deaths'],
                'roshan_kills': msg['roshan_kills'],
                'tower_kills': msg['tower_kills'],

                'base_damage': (msg['damage_max'] + msg['damage_min'])/2,
                'bonus_damage': msg['damage_bonus'],
                'total_damage': (
                        msg['damage_max'] + msg['damage_min']
                    )/2 + msg['damage_bonus'],
                'healing': msg['healing'],

                'reliable_gold': msg['reliable_gold'],
                'unreliable_gold': msg['unreliable_gold'],
                'shared_gold': msg['shared_gold'],
                'total_earned_gold': msg['total_earned_gold'],
                'creep_kill_gold': msg['creep_kill_gold'],
                'hero_kill_gold': msg['hero_kill_gold'],
                'income_gold': msg['income_gold'],

                'lifestate': msg['lifestate'],
                'respawn_time': msg['respawn_time'],
                'xp': msg['xp'],
            }
            for msg in msgs
            if msg['hero_id'] == pms.hero.steam_id
            if set([
                'agility',
                'agility_total',
                'armor',
                'assists',
                'creep_kill_gold',
                'damage_bonus',
                'damage_max',
                'damage_max', 'damage_min',
                'deaths',
                'denies',
                'healing',
                'health',
                'health',
                'hero_kill_gold',
                'income_gold',
                'intelligence',
                'intelligence_total',
                'kills',
                'last_hits',
                'lifestate',
                'mana',
                'mana',
                'max_health',
                'max_mana',
                'misses',
                'nearby_creep_deaths',
                'reliable_gold',
                'respawn_time',
                'roshan_kills',
                'shared_gold',
                'strength',
                'strength_total',
                'total_earned_gold',
                'tower_kills',
                'unreliable_gold',
                'xp',
            ]).issubset(set(msg.keys()))
        ],
        key=lambda x: x['offset_time']
    )


# Needs to add on items.  Probably worth ignoring.
# 'magic_resist_pct'

# What is this even?
# 'recent_damage'

# Is this even valid?   Doesn't seem to return nonzero
# 'damage_taken'


def safe_pct(numerator, denominator):
    if denominator == 0:
        return 0
    else:
        return float(numerator)/denominator
