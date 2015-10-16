var kills = function(icon){
    var icon = icon;

    return function(msg){

      return msg.type == "kills" &&
      msg.unit == icon.hero.internal_name && // Is hero
      msg.key.substring(0,14) == 'npc_dota_hero_' && // Kills hero
      msg.target_illusion==false &&
      msg.target_hero==true &&
      msg.side !== icon.side;
    };
}


module.exports = {
    kills: kills
}
