'use strict';

var pms_merge = function(data, pmses){
  return data.map(function (d){

    var pms = pmses.filter(
        function(p){
            return p.hero.internal_name === d[0].unit;
        }
    )[0];
    pms.key_name = pms.hero.name;
    return {
        icon: pms,
        values: d
    };
  });
};

var sides = function(data){

  var foo =  ['Radiant', 'Dire'].map(function(side){

      var side_data = data.filter(function(d){
        return d.icon.side === side;
      }).reduce(function(a, b){
        return a.concat(b.values);
      }, []);

      // var new_icon = d.icon;
      // new_icon.key_name = side;

      return {
        icon: {
          side: side,
          key_name: side,
        },
        values: side_data.sort(function(a, b){
            return a.offset_time - b.offset_time;
        })
      };
  });
  return foo;
};

var matches = function(data){

  var match_id_list = unique(
    data.map(function(d){
      return d.icon.match.steam_id;
    })
  );

  var foo = match_id_list.map(function(steam_id){

      var match_data = data.filter(function(d){
        return d.icon.match.steam_id === steam_id;
      }).reduce(function(a, b){
        return a.concat(b.values);
      }, []);

      return {
        icon: {
            key_name: 'Match #'+steam_id
        },
        values: match_data.sort(function(a,b){
            return a.offset_time - b.offset_time;
        })
      }
  });

  return foo;

};


var noop = function(data){
    return data;
};

var unique = function(arr) {
    var u = {}, a = [];
    for(var i = 0, l = arr.length; i < l; ++i){
        if(!u.hasOwnProperty(arr[i])) {
            a.push(arr[i]);
            u[arr[i]] = 1;
        }
    }
    return a;
};

module.exports = {
    pms_merge: pms_merge,
    sides: sides,
    noop: noop,
    matches: matches,
}
