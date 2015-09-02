"use strict";

var extract_pickbans = function(blanks, working_set){
    var data = JSON.parse(JSON.stringify(blanks));
    working_set.map(function(match){
      var pickbans = match.pickbans;

      pickbans.map(function(pickban){
        var steam_id = pickban.hero.steam_id;
        var is_win = (
          match.radiant_win && pickban.team === 0 ||
          !match.radiant_win && pickban.team === 1
          );

        if (data.values[steam_id] === undefined){
          data.values[steam_id] = {
            picks: 0,
            bans: 0,
            wins: 0,
            losses: 0,
            hero: pickban.hero
          };
        }

        if (pickban.is_pick){
          if(is_win){
            data.values[steam_id].wins +=1;
          } else {
            data.values[steam_id].losses +=1;
          }
          data.values[steam_id].picks += 1;
        } else {
          data.values[steam_id].bans += 1;
        }
      });
    });

    // Because nvd3 has baked-in assumptions about values being an array starting at 0.
    var values = [];
    data.values.map(function(d){
        if (d !== null){
          values.push(d);
        }
    });
    data.values = values;
    return [data];
};

module.exports = {
  extract_pickbans: extract_pickbans
};
