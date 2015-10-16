'use strict';

var pms_merge = function(data, pmses){
  return data.map(function (d){

    var pms = pmses.filter(
        function(p){
            return p.hero.internal_name === d[0].unit;
        }
    )[0];

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

      return {
        icon: {
            name: side
        },
        values: side_data.sort(function(a,b){
            return a.offset_time - b.offset_time;
        })
      }
  });
  return foo;
};

var noop = function(data){
    return data;
};

module.exports = {
    pms_merge: pms_merge,
    sides: sides,
    noop: noop,
}
