"use strict";

var kills = function(icon){

    return function(msg){
      return msg.type === "kills" &&
      msg.unit === icon.hero.internal_name && // Is hero
      msg.key.substring(0,14) === 'npc_dota_hero_' && // Kills hero
      msg.target_illusion === false &&
      msg.target_hero === true &&
      msg.side !== icon.side;
    };
};

var all_gold = function(icon){
    return function(msg){
      return msg.type === "gold_reasons";
    };
};

var earned_gold = function(icon){
    return function(msg){
      return msg.type === "gold_reasons" && msg.key !=="6";
    };
};


var xp = function(icon){
    return function(msg){
      return msg.type === "xp_reasons";
    };
};

var healing = function(icon){
    return function(msg){
      return msg.type === "healing";
    };
};


module.exports = {
    kills: kills,
    all_gold: all_gold,
    xp: xp,
    healing: healing,
    earned_gold: earned_gold,
}
