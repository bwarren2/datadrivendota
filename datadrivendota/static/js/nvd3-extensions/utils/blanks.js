var blank_hero_pickbans = function(dossiers){
    var return_obj = {};
    var values_ary = [];
    var test = dossiers.map(function(h){
    var steam_id = h.hero.steam_id;
    values_ary[steam_id] = {
        picks: 0,
        bans: 0,
        wins: 0,
        losses: 0,
        hero: h.hero
        };
    });
    return_obj['key'] = 'Winrate';
    return_obj['values'] = values_ary;
    return return_obj;
}

module.exports = {
    blank_hero_pickbans: blank_hero_pickbans
}
