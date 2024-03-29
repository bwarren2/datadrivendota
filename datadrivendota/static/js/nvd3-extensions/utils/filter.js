'use strict';


// These are getting weird, ie three functions deep, because they are special.
// These are called in template to curry a function with the time value.
// Then the fn is called in the shard_charting general-purpose fn as normal.

var time_gte = function(time){

  return function(icon){
    return function(msg){
      return msg.offset_time >= time;
    };
  };

};

var time_lte = function(time){

  return function(icon){
    return function(msg){
      return msg.offset_time <= time;
    };
  };

};

// End weird fns

var last_hits = function(icon){
    var name_length = icon.hero.internal_name.length;
    return function(msg){
      return msg.type === 'kills' &&
      msg.unit.slice(0, name_length) === icon.hero.internal_name && // Is hero
      msg.key.substring(0,14) !== 'npc_dota_hero_' && // Doesn't kill hero
      msg.side !== icon.side;
    };
};


var kills = function(icon){

    return function(msg){
      return msg.type === 'kills' &&
      msg.unit === icon.hero.internal_name && // Is hero
      msg.key.substring(0,14) === 'npc_dota_hero_' && // Kills hero
      msg.target_illusion === false &&
      msg.target_hero === true &&
      msg.side !== icon.side;
    };
};

var deaths = function(icon){

    return function(msg){
      return msg.type === 'kills' &&
      msg.key === icon.hero.internal_name && // Is hero
      msg.unit.substring(0,14) === 'npc_dota_hero_' && // Kills hero
      msg.target_illusion === false &&
      msg.target_hero === true &&
      msg.side !== icon.side;
    };
};

var key_bldg_dmg_dealt = function(icon){
    return function(msg){
      // console.log(msg.side);
      if (icon.side === 'Radiant'){
        return msg.type === 'damage' &&
        msg.unit === icon.hero.internal_name && // Is hero
        dire_key_buildings.indexOf(msg.key) !== -1; // Kills building
      } else {
        return msg.type === 'damage' &&
        msg.unit === icon.hero.internal_name && // Is hero
        radiant_key_buildings.indexOf(msg.key) !== -1; // Kills building

      }
    };
};

var key_bldg_kills = function(icon){
    return function(msg){
      // console.log(msg.side);
      if (icon.side === 'Radiant'){
        return msg.type === 'kills' &&
        dire_key_buildings.indexOf(msg.key) !== -1; // Kills building
      } else {
        return msg.type === 'kills' &&
        radiant_key_buildings.indexOf(msg.key) !== -1; // Kills building

      }
    };
};


var hero_dmg_dealt = function(icon){

    return function(msg){
      return msg.type === 'damage' &&
      msg.unit === icon.hero.internal_name && // Is hero
      msg.key.substring(0,14) === 'npc_dota_hero_' && // Kills hero
      msg.target_illusion === false &&
      msg.target_hero === true &&
      msg.side !== icon.side;
    };
};

var hero_dmg_taken = function(icon){

    return function(msg){
      return msg.type === 'damage' &&
      msg.key === icon.hero.internal_name && // Is hero
      msg.unit.substring(0,14) === 'npc_dota_hero_' && // Kills hero
      msg.target_illusion === false &&
      msg.target_hero === true &&
      msg.side !== icon.side;
    };
};

var other_dmg_dealt = function(icon){

    return function(msg){
      return msg.type === 'damage' &&
      msg.unit === icon.hero.internal_name && // Is hero
      msg.key.substring(0,14) !== 'npc_dota_hero_' && // Kills hero
      msg.side !== icon.side;
    };
};

var other_dmg_taken = function(icon){

    return function(msg){
      return msg.type === 'damage' &&
      msg.key !== icon.hero.internal_name && // Is hero
      msg.unit.substring(0,14) === 'npc_dota_hero_' && // Kills hero
      msg.side !== icon.side;
    };
};


var all_gold = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons';
    };
};

var earned_gold = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key !=='6';
    };
};

var death_expense = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '1';
    };
};

var buyback_expense = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '2';
    };
};

var building_income = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '11';
    };
};

var hero_kill_income = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '12';
    };
};

var creep_kill_income = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '13';
    };
};

var roshan_kill_income = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '14';
    };
};

var courier_kill_income = function(icon){
    return function(msg){
      return msg.type === 'gold_reasons' && msg.key === '15';
    };
};


var xp = function(icon){
    return function(msg){
      return msg.type === 'xp_reasons';
    };
};

var hero_xp = function(icon){
    return function(msg){
      return msg.type === 'xp_reasons' && msg.key === '1';
    };
};

var creep_xp = function(icon){
    return function(msg){
      return msg.type === 'xp_reasons' && msg.key === '2';
    };
};

var roshan_xp = function(icon){
    return function(msg){
      return msg.type === 'xp_reasons' && msg.key === '3';
    };
};

var healing = function(icon){
    return function(msg){
      return msg.type === 'healing';
    };
};

var item_buys = function(icon){
    return function(msg){
      return msg.type === 'purchase';
    };
};


var radiant_key_buildings = [
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

var dire_key_buildings = [
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

module.exports = {
    kills: kills,
    deaths: deaths,
    all_gold: all_gold,
    xp: xp,
    healing: healing,
    earned_gold: earned_gold,
    hero_dmg_taken: hero_dmg_taken,
    hero_dmg_dealt: hero_dmg_dealt,
    other_dmg_taken: other_dmg_taken,
    other_dmg_dealt: other_dmg_dealt,
    time_gte: time_gte,
    time_lte: time_lte,
    last_hits: last_hits,
    building_income: building_income,
    buyback_expense: buyback_expense,
    courier_kill_income: courier_kill_income,
    creep_kill_income: creep_kill_income,
    death_expense: death_expense,
    hero_kill_income: hero_kill_income,
    roshan_kill_income: roshan_kill_income,
    hero_xp: hero_xp,
    creep_xp: creep_xp,
    roshan_xp: roshan_xp,
    key_bldg_dmg_dealt: key_bldg_dmg_dealt,
    key_bldg_kills: key_bldg_kills,
    item_buys: item_buys,
}
