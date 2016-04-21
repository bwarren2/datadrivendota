(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.d7 = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict";

function AjaxCache() {
    this.cache = {};
}

AjaxCache.prototype.get = function (path) {
    var self = this;  // Just in case the Promise.resolve call screws with `this`.
    if (self.cache.hasOwnProperty(path)) {
        return Promise.resolve(self.cache[path]);
    } else {
        self.cache[path] = $.ajax(path);
        return self.cache[path];
    }
}

var aj = new AjaxCache();

module.exports = aj;

},{}],2:[function(require,module,exports){
module.exports = {
  classDiscreteBarChart: function(destination, plot_data){

      var svg = window.make_svg(destination);

      var chart = nv.models.discreteBarChart();

      chart.x(function(d){return d.label;})
            .y(function(d){return d.value;})
            .margin({
              bottom:120
            });

      svg.datum(plot_data)
        .transition()
        .duration(500)
        .call(chart);

      d3.select(destination + " .nv-x.nv-axis > g")
        .selectAll("g")
        .selectAll("text")
        .attr("transform", function(d,i,j) { return "translate (-7, 65) rotate(-90 0,0)"; }) ;

      return chart;

  }
}

},{}],3:[function(require,module,exports){
"use strict";
var utils = require("../utils");
var AjaxCache = require("../ajax_cache");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var tooltips = require("./tooltips.js");

var classify_points = function(destination){
  var place = destination + " circle.nv-point";
  d3.selectAll(place).attr(
    "class",
    function(d){
        var hero = d[0].hero;
        return d3.select(this).attr("class") + " hero-datum "+ hero.css_classes;
    }
  ).attr(
    "data-hero",
    function (d) {
      // Hacky as hell, but I don't want to make backend changes right now.
      // --kit 2015-09-02
      return d[0].hero.css_classes.split(' ')[0];
    }
  );
};

var classify_bars = function(destination){

  var place = destination + " rect.discreteBar";
  d3.selectAll(place).attr(
    "class",
    function(d){
        var hero = d.hero;
        return d3.select(this).attr("class")+ " hero-datum "+hero.css_classes;
    }
  ).attr(
    "data-hero",
    function (d) {
      // Hacky as hell, but I don't want to make backend changes right now.
      // --kit 2015-09-02
      return d.hero.css_classes.split(' ')[0];
    }
  );
}


var pickban_scatter = function(destination, params, display_final_product){

  var winrate_data;
  var dossiers;
  var blanks;
  Promise.all([
    AjaxCache.get(
      "/rest-api/match-pickban/?" + $.param(params)
    ),
    AjaxCache.get(
      "/rest-api/hero-dossiers/"
    )
  ]).then(function(data){

    winrate_data = data[0];
    dossiers = data[1];
    blanks = utils.blanks.blank_hero_pickbans(dossiers);

    var idx;
    if (display_final_product !== undefined){
      idx = winrate_data.length;
    } else {
      idx = 0;
    }

    $(destination).empty();
    return winrate_data.slice(0, idx);
  })
  .then(function(working_set){
    var plot_data = d7.extensions.utils.reduce.extract_pickbans(
      blanks, working_set
    );
    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    var xlab = "# Games Banned";
    var ylab = "# Games Picked";
    nv.addGraph(

      function(){

        chart = models.scatter_chart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .x(function(d){return d.bans;})
          .y(function(d){return d.picks;})
          .showLegend(false);


        chart.contentGenerator(
          tooltips.hero_tooltip(
            function(a){return a.bans;},
            function(a){return a.picks;},
            xlab,
            ylab
          )
        );

        chart.xAxis.axisLabel(xlab);
        chart.yAxis.axisLabel(ylab).axisLabelDistance(-20);

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      },

      function(chart){

        classify_points(destination);

        $(window).on(
          "update",
          function(e, p1){
            var new_data = d7.extensions.utils.reduce.extract_pickbans(
              blanks, winrate_data.slice(0, p1)
            );
            var chart_data = svg.datum(new_data);
            chart_data.transition().duration(500).call(chart);
          }
        );

      }

    );

  }).catch(function(e){
    console.log(e);
  });
};


var winrate_scatter = function(destination, params, display_final_product){

  var winrate_data;
  var dossiers;
  var blanks;

  Promise.all([
    $.ajax(
      "/rest-api/match-pickban/?" + $.param(params)
    ),
    $.ajax(
      "/rest-api/hero-dossiers/"
    )
  ]).then(function(data){
    winrate_data = data[0];
    dossiers = data[1];
    blanks = utils.blanks.blank_hero_pickbans(dossiers);


    var idx;
    if (display_final_product !== undefined){
      idx = winrate_data.length;
    } else {
      idx = 0;
    }

    $(destination).empty();
    return winrate_data.slice(0, idx);

  })
  .then(function(working_set){
    var plot_data = d7.extensions.utils.reduce.extract_pickbans(
      blanks, working_set
    );
    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    var xlab = "# Games Picked";
    var ylab = "Win %";

    nv.addGraph(

      function(){
        chart = models.scatter_chart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .x(function(d){
            return d.picks;
          })
          .y(function(d){
            if (d.wins + d.losses === 0) return 0;
            else { return 100 * d.wins / (d.wins + d.losses); }
          })
          .showLegend(false);


        chart.contentGenerator(
          tooltips.hero_tooltip(
            function(d){
              return d.picks;
            },
            function(d){
              if (d.wins + d.losses === 0) return 0;
              else { return (100 * d.wins / (d.wins + d.losses)).toFixed(2); }
            },
            xlab,
            ylab
          )
        );

        chart.xAxis.axisLabel(xlab);
        chart.yAxis.axisLabel(ylab).axisLabelDistance(-20);

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      },

      function(chart){

        classify_points(destination);

        $(window).on(
          "update",
          function(e, p1){
            var new_data = d7.extensions.utils.reduce.extract_pickbans(
              blanks, winrate_data.slice(0, p1)
            );
            var chart_data = svg.datum(new_data);
            chart_data.transition().duration(500).call(chart);
          }
        );

      }

    );

  }).catch(function(e){
    console.log(e);
  });
};

var quality_barchart = function(destination, params, display_final_product){

  var winrate_data;
  var dossiers;
  var blanks;

  Promise.all([
    $.ajax(
      "/rest-api/match-pickban/?" + $.param(params)
    ),
    $.ajax(
      "/rest-api/hero-dossiers/"
    )
  ]).then(function(data){
    winrate_data = data[0];
    dossiers = data[1];
    blanks = utils.blanks.blank_hero_pickbans(dossiers);
    $(destination).empty();

    var idx;
    if (display_final_product !== undefined){
      idx = winrate_data.length;
    } else {
      idx = 0;
    }

    return winrate_data.slice(0, idx);

  })
  .then(function(working_set){
    var plot_data = d7.extensions.utils.reduce.extract_pickbans(
      blanks, working_set
    );
    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    var xlab = "Hero";
    var ylab = "Relative Strength";
    var strength = function(hero){
      if (hero.wins + hero.losses === 0){return 0;}
      else{
        var z = 1.97;
        var n = hero.wins + hero.losses;
        var phat = 1.0*hero.wins/n;
        return (phat + z*z/(2*n) - z * Math.sqrt((phat*(1-phat)+z*z/(4*n))/n))/(1+z*z/n)
      }
    }

    nv.addGraph(

      function(){
        chart = models.discrete_bar_chart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .x(function(d){return d.hero.name;})
          .y(function(d){return strength(d);})
          .showXAxis(false);

        chart.xAxis.axisLabel(xlab);
        chart.yAxis.axisLabel(ylab).axisLabelDistance(-20);

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      },

      function(chart){

        classify_bars(destination);
        $(window).on(
          "update",
          function(e, p1){
            var new_data = d7.extensions.utils.reduce.extract_pickbans(
              blanks, winrate_data.slice(0, p1)
            );
            var chart_data = svg.datum(new_data);
            chart_data.transition().duration(500).call(chart);
          }
        );

      }

    );

  }).catch(function(e){
    console.log(e);
  });
};


module.exports = {
  pickban_scatter: pickban_scatter,
  winrate_scatter: winrate_scatter,
  quality_barchart: quality_barchart,
};

},{"../ajax_cache":1,"../models":14,"../utils":20,"./tooltips.js":8}],4:[function(require,module,exports){
module.exports = {
    heroes: require('./heroes.js'),
    matches: require('./matches.js'),
    bar: require('./bar.js'),
    pms_shards: require('./pms_replay_shards.js'),
    replays: require('./replays.js'),
}

},{"./bar.js":2,"./heroes.js":3,"./matches.js":5,"./pms_replay_shards.js":6,"./replays.js":7}],5:[function(require,module,exports){
"use strict";

var utils = require("../utils");
var models = require("../models");
var AjaxCache = require("../ajax_cache");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var moment = window.moment;
var tooltips = require("./tooltips.js");

var pms_scatter = function(destination, params, x_var, y_var, x_lab, y_lab){

  Promise.resolve(
    AjaxCache.get(
      "/rest-api/player-match-summary/?" + $.param(params)
    )
  ).then(function(pmses){
    $(destination).empty();

    var plot_data = [
        {
          "key": 'Radiant',
          "values": pmses.filter(function(d){
            return d.side === 'Radiant';
          }).map(function(d){
              var foo = {}
              foo[x_var] = d[x_var]
              foo[y_var] = d[y_var]
              foo.hero = d.hero
              return foo
          })
        },       {
          "key": 'Dire',
          "values": pmses.filter(function(d){
            return d.side === 'Dire';
          }).map(function(d){
              var foo = {}
              foo[x_var] = d[x_var]
              foo[y_var] = d[y_var]
              foo.hero = d.hero
              return foo
          })
        }
    ]

    var chart;
    var chart_data;

    var svg = utils.svg.square_svg(destination);
    nv.addGraph(
      function(){

        chart = models.scatter_chart()
          .margin({
            left: 60,
            bottom: 45,
          })
          .x(function(d){return d[x_var];})
          .y(function(d){return d[y_var];})
          .showLegend(false);


        chart.contentGenerator(
          tooltips.hero_tooltip(
            function(a){return a[x_var];},
            function(a){return a[y_var];},
            x_lab,
            y_lab
          )
        );

        chart.xAxis.axisLabel(x_lab);
        chart.yAxis.axisLabel(y_lab).axisLabelDistance(-5).tickFormat(
          utils.axis_format.pretty_numbers
        );

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      },

      function(){
        svg.select(destination + " .axis").selectAll("text").remove();

        var ticks = svg.select(".axis").selectAll(".tick")
            .data(plot_data)
            .append("svg:image")
            .attr("xlink:href", function (d) {
              return d.img ;
            })
            .attr("width", 100)
            .attr("height", 100);

        var width = $(destination).width();
        var height = $(destination).height();

        var face_data = plot_data[0].values.map(function(d){
          d.faceclass='radiant-face-glow'
          return d
        })
        .concat(
          plot_data[1].values.map(function(d){
          d.faceclass='dire-face-glow'
          return d
          })
        );

        var plot_faces = d3.select(destination).selectAll('i').data(
            face_data
          )
          .enter()
          .append('i')
          .attr('class', function(d){
            return 'd2mh ' + d.hero.internal_name + ' ' + d.faceclass
          })
          .style('left', function(d){
            var px = chart.xAxis.scale()(d[x_var])+chart.margin().left-2
            return px+'px';
          })
          .style('top', function(d){
            var px = chart.yAxis.scale()(d[y_var])+50
            return px+'px'
          })
          .style('position', 'absolute')

      }

    );

  }).catch(function(e){
    console.log(e);
  });
};

var kill_death_scatter = function(destination, params){
    pms_scatter(destination, params, "kills", "deaths", "Kills", "Deaths");
};

var kill_dmg_scatter = function(destination, params){
    pms_scatter(destination, params, "kills", "hero_damage", "Kills", "Hero Damage");
};

var xpm_gpm_scatter = function(destination, params){
    pms_scatter(destination, params, "gold_per_min", "xp_per_min", "Gold/min", "XP/min");
};

var lh_denies_scatter = function(destination, params){
    pms_scatter(destination, params, "last_hits", "denies", "Last Hits", "Denies");
};

var ability_lines = function(destination, params){
    Promise.resolve(
    AjaxCache.get(
      "/rest-api/player-match-summary/?" + $.param(params)
    )
  ).then(function(pmses){
    $(destination).empty();
    var plot_data = pmses.map(function(pms){
      return {
        "key": pms.hero.name,
        values: pms.skillbuild.map(function(d){
          return {
            y: d.level,
            x: d.time,
          };
        })
      }
    });

    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    nv.addGraph(
      function(){

        chart = nv.models.lineWithFocusChart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .showLegend(true);

        chart.xAxis.axisLabel("Time").tickFormat(
          utils.axis_format.pretty_times
        );
        chart.yAxis.axisLabel("Level");

        chart.x2Axis.tickFormat(
          utils.axis_format.pretty_times
        );

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      }

    );

  }).catch(function(e){
    console.log(e);
  });

};

var pms_bar_chart = function(destination, params, y_var, y_lab){
    Promise.resolve(
    AjaxCache.get(
      "/rest-api/player-match-summary/?" + $.param(params)
    )
  ).then(function(pmses){
    $(destination).empty();
    var plot_data = [{
        "key": y_lab,
        values: pmses.map(function(d){
          if (d.side=='Dire'){
            var faceclass = 'dire-face-glow'
          } else{
            var faceclass = 'radiant-face-glow'
          }
          return {
            y: d[y_var],
            x: d.hero.name,
            hero: d.hero,
            faceclass: faceclass
          };
        })
      }]
    ;

    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    nv.addGraph(
      function(){

        chart = nv.models.discreteBarChart()
          .margin({
            left: 45,
            bottom: 45,
          });

        chart.xAxis.axisLabel();
        chart.yAxis.axisLabel(y_lab).tickFormat(
          utils.axis_format.pretty_numbers
        );

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);

        return chart;
      },
      function(){
        d3.select(destination + " .nv-x.nv-axis > g :not(.nv-axislabel)")
          .selectAll("g")
          .selectAll("text")
          .remove();

        var face_data = plot_data[0].values;

        var plot_faces = d3.select(destination).selectAll('i').data(
            face_data
          )
          .enter()
          .append('i')
          .attr('class', function(d){
            return 'd2mh ' + d.hero.internal_name + ' ' + d.faceclass
          })
          .style('left', function(d){
            var px = chart.xScale()(d.x)+chart.margin().left+10
            return px+'px';
          })

          .style('bottom', function(d){
            var px = chart.margin().bottom-15
            return px+'px';
          })
          .style('position', 'absolute')


      }

    );

  }).catch(function(e){
    console.log(e);
  });

};

var lh_barchart = function(destination, params){
    pms_bar_chart(destination, params, "last_hits", "Last Hits");
};

var kda2_barchart = function(destination, params){
    pms_bar_chart(destination, params, "kda2", "K-D+A/2");
};

var tower_dmg_barchart = function(destination, params){
    pms_bar_chart(destination, params, "tower_damage", "Tower Damage");
};


var match_timeline = function(destination, params){

  Promise.resolve(
    AjaxCache.get(
      "/rest-api/matches/?" + $.param(params)
    )
  ).then(function(data){
    $(destination).empty();

    var data = [{
      key: "Matches",
      values: data
    }];

    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    nv.addGraph(
      function(){

        chart = models.scatter_chart()
          .margin({
            left: 60,
            right: 60,
            bottom: 45,
          })
          .x(function(d){return d.start_time;})
          .y(1)
          .showLegend(false)
          .showYAxis(false);

        chart.xAxis.axisLabel("")
          .tickFormat(function(d){
            return moment.unix(d).format("MM/DD/YYYY");
           })
          .ticks(5);
          chart.xAxis.showMaxMin(false);

        chart.yAxis.axisLabel("");


        chart.contentGenerator(
          tooltips.match_tooltip
        );


        chart_data = svg.datum(data);
        chart_data
          .transition()
          .duration(500)
          .call(chart);

        return chart;
      }

    );



  });
};


module.exports = {
  pms_scatter: pms_scatter,
  kill_death_scatter: kill_death_scatter,
  kill_dmg_scatter: kill_dmg_scatter,
  xpm_gpm_scatter: xpm_gpm_scatter,
  lh_denies_scatter: lh_denies_scatter,
  ability_lines: ability_lines,
  lh_barchart: lh_barchart,
  kda2_barchart: kda2_barchart,
  tower_dmg_barchart: tower_dmg_barchart,
  match_timeline: match_timeline,
};

},{"../ajax_cache":1,"../models":14,"../utils":20,"./tooltips.js":8}],6:[function(require,module,exports){
"use strict";
var utils = require("../utils");
var components = require("../components");
var AjaxCache = require("../ajax_cache");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var _ = window._;
var tooltips = require("./tooltips.js");

var endcap = function(data){
  var min_time = d3.min(data, function(data_obj){
    return d3.min(data_obj.values, function(datum){
      return datum.offset_time;
    });
  });
  var max_time = d3.max(data, function(data_obj){
    return d3.max(data_obj.values, function(datum){
      return datum.offset_time;
    });
  });

  data.forEach(function(d){
    if(d.values.length>0){
      var left_msg = {
        offset_time: min_time,
        sum: 0,
      };
      var right_msg = {
        offset_time: max_time,
        sum: undefined,
      };

      right_msg.sum = d.values[d.values.length-1].sum;

      d.values.push(right_msg);
      d.values.unshift(left_msg);
    }
  });
  return data;
};

var plot_shard_lineup = function(
    data,
    msg_filters,
    msg_map,
    msg_reshape,
    x_data,
    y_data,
    destination,
    pmses,
    params
  ){

  // Clear the div
  $(destination).empty();

  data = utils.reshape.pms_merge(data, pmses);

  data = data.map(function(d){

    var data_values = d.values;

    for (var i = 0; i < msg_filters.length; i++){
      data_values = data_values.filter(
        msg_filters[i](d.icon)
      );
    }

    return {
      icon: d.icon,
      values: data_values
    };
  });

  // Reshape into something else if needed.
  data = msg_reshape(data);

  data = _.cloneDeep(data);

  // Filter, map, cast data into plotting format
  var plot_data = data.map(function(d){
    return {
      "key": d.icon.key_name,
      "values": d.values.map(msg_map(d.icon))
    };
  });
  plot_data = endcap(plot_data);

  render_data(
    destination,
    plot_data,
    x_data,
    y_data,
    params
  );

};

var render_data = function(
    destination,
    plot_data,
    x_data,
    y_data,
    params
  ){
  $(destination).empty();

  var width;
  var height;

  if(params!==undefined){
    if(params.height!==undefined){
      height = params.height;
    }
    if(params.width!==undefined){
      width = params.width;
    }
  }

  var svg = utils.svg.square_svg(destination, width, height);
  nv.addGraph(

    function(){
      var chart = nv.models.lineChart()
        .margin({
          left: 45,
          bottom: 45,
        })
        .x(x_data.access)
        .y(y_data.access)
        .showLegend(false)
        .interpolate("step-after")
        .forceY(0);

      if(params !== undefined){

        if(params.height!==undefined){
          chart.height(params.height);
        }
        if(params.width!==undefined){
          chart.width(params.width);
        }
        if(params.forceY!==undefined){
          chart.forceY(params.forceY);
        }
        if(params.forceX!==undefined){
          chart.forceX(params.forceX);
        }
        if(params.contentGenerator!==undefined){
          chart.tooltip.contentGenerator(params.contentGenerator);
        }
      }


      chart.xAxis.axisLabel(x_data.label).tickFormat(
        function(d){
          return String(d).toHHMMSS();
        }
      );
      chart.yAxis.axisLabel(y_data.label).axisLabelDistance(-18).tickFormat(
        function(d){
          if(d>1000000){return (d/1000000).toFixed(0) + "M";}
          else if(d>1000){return (d/1000).toFixed(0) + "K";}
          else { return d; }
        }
      );

      var chart_data = svg.datum(plot_data);
      chart_data.transition().duration(500).call(chart);
      return chart;
    }
  );
}

var shard_lineup = function(
  pms_ids,
  msg_filters,
  msg_map,
  msg_reshape,
  x_data,
  y_data,
  destination
){

  var url ="/rest-api/player-match-summary/?ids=["+pms_ids.toString()+"]";
  var pmses;

  // Get the PMS info
  Promise.resolve(
    AjaxCache.get({
      url: url,
      dataType: "json"
    })

  ).then(function(data){

    pmses = data;

    // Get their replays
    return Promise.all(
      data.map(function(pms){
        return Promise.resolve(
          $.ajax({
            url: pms.replay_shard,
            dataType: "json",
          })
        );
      })
    );
  }).then(function(data){

    plot_shard_lineup(
      data,
      msg_filters,
      msg_map,
      msg_reshape,
      x_data,
      y_data,
      destination,
      pmses
    );
  }).catch(function(e){
    console.log(e);
  });
};

// Used for the ESL 1 blog feature.
var special_shard_lineup = function(match_id){

  var url ="/rest-api/player-match-summary/?match_id="+match_id;
  var pmses;

  // Get the PMS info
  Promise.resolve(
    AjaxCache.get({
      url: url,
      dataType: "json"
    })

  ).then(function(data){

    pmses = data;

    // Get their replays
    return Promise.all(
      data.map(function(pms){
        return Promise.resolve(
          $.ajax({
            url: pms.replay_shard,
            dataType: "json",
          })
        );
      })
    );
  }).then(function(data){

    $("button#draw").on("click", function(){

        var rollup_map = {
            player: utils.reshape.noop,
            side: utils.reshape.sides,
            match: utils.reshape.matches,
        };
        var rollup_fn = rollup_map[$("select#rollup ").val()];
        var chart_destination = "#"+$("select#destination").val()+" .chart";

        var label_destination = "#"+$("select#destination").val()+" label";
        var label = $("select#data option:selected ").html()+' by '+$("select#rollup option:selected ").html();
        $(label_destination).html(label);

        var data_map = {
            kills: utils.filter.kills,
            deaths: utils.filter.deaths,
            last_hits: utils.filter.last_hits,
            hero_dmg_dealt: utils.filter.hero_dmg_dealt,
            hero_dmg_taken: utils.filter.hero_dmg_taken,
            other_dmg_dealt: utils.filter.other_dmg_dealt,
            other_dmg_taken: utils.filter.other_dmg_taken,
            earned_gold: utils.filter.earned_gold,
            all_gold: utils.filter.all_gold,
            xp: utils.filter.xp,
            healing: utils.filter.healing,
            building_income: utils.filter.building_income,
            buyback_expense: utils.filter.buyback_expense,
            courier_kill_income: utils.filter.courier_kill_income,
            creep_kill_income: utils.filter.creep_kill_income,
            death_expense: utils.filter.death_expense,
            hero_kill_income: utils.filter.hero_kill_income,
            roshan_kill_income: utils.filter.roshan_kill_income,
            hero_xp: utils.filter.hero_xp,
            creep_xp: utils.filter.creep_xp,
            roshan_xp: utils.filter.roshan_xp,
        };

        var data_fn = data_map[$("select#data ").val()];
        var start_time = $("#start_time").val();
        var end_time = $("#end_time").val();
        var timeToSecs = function(time){
            return parseInt(time.split(":")[0])*60+parseInt(time.split(":")[1]);
        };

        if(start_time!==""){
            start_time = timeToSecs(start_time);
        } else{
            start_time = -10000;
        }

        if(end_time!==""){
            end_time = timeToSecs(end_time);
        } else{
            end_time = 100000;
        }

        var selected_data = [];
        $("form input:checked").each(function() {
            var id = $(this).attr("value");
            selected_data.push(data[parseInt(id)]);
        });

        plot_shard_lineup(
          selected_data,
          [
            data_fn,
            utils.filter.time_gte(start_time),
            utils.filter.time_lte(end_time),
          ],
          utils.map.sum,
          rollup_fn,
          components.axes.offset_time,
          components.axes.sum,
          chart_destination,
          pmses
        );

    });


  }).catch(function(e){
    console.log(e);
  });
};


var state_lineup = function(pms_ids, facet, destination, params){

  var url_base ="/rest-api/statelog/?pms_id=";
  var pmses;
  // Get the PMS info
  Promise.all(
    pms_ids.map(function(pms_id){
      var url = url_base+pms_id;
      return $.getJSON(url);
    })
  ).then(function(data){
    pmses = data.map(function(d){
      return d[0].playermatchsummary;
    });

    Promise.all(
      data.map(function(pms){
        var location = pms[0][facet];
        return $.getJSON(location);
      })
    ).then(function(facets){

      // Structure the fancy filtering we are about to do.

      var timeToSecs = function(time){
          return parseInt(time.split(":")[0])*60+parseInt(time.split(":")[1]);
      };

      var width;
      var height;
      var start_time;
      var end_time;
      var interpolation;
      var granularity;
      if(params!==undefined){

        if(params.start_time!==undefined&params.start_time!==""){
          start_time = timeToSecs(params.start_time);
        } else {
          start_time = -10000;
        }

        if(params.end_time!==undefined&params.end_time!==""){
          end_time = timeToSecs(params.end_time);
        } else {
          end_time = 10000;
        }

        if(params.interpolation!==undefined){
          interpolation = params.interpolation;
        } else {
          interpolation = "step-after";
        }

        if(params.granularity!==undefined){
          granularity = params.granularity;
        } else {
          granularity = 10;
        }

      }



      var plot_data = facets.map(function(d, i){
        var filtered_dataset = d.filter(function(x){
          return x.offset_time <= end_time & x.offset_time >= start_time;
        }).filter(function(x){
          return x.offset_time.mod(granularity) === 0;
        });
        return {
          key: pmses[i].hero.name,
          values: filtered_dataset,
        }
      });

      $(destination).empty();

      var make_axis = function(name){
        return {
          access: function(d){
            return d[name];
          },
          label: toTitleCase(name.replace(/\_/g, " "))
        }
      };

      var x_data = make_axis("offset_time");
      var y_data = make_axis(facet);


      var svg = utils.svg.square_svg(destination, width, height);
      nv.addGraph(

        function(){
          var chart = nv.models.lineChart()
            .margin({
              left: 45,
              bottom: 45,
            })
            .x(x_data.access)
            .y(y_data.access)
            .showLegend(false)
            .interpolate(interpolation)
            .forceY(0);

          if(params !== undefined){

            if(params.height!==undefined){
              chart.height(params.height);
            }
            if(params.width!==undefined){
              chart.width(params.width);
            }
            if(params.forceY!==undefined){
              chart.forceY(params.forceY);
            }
            if(params.forceX!==undefined){
              chart.forceX(params.forceX);
            }
            if(params.contentGenerator!==undefined){
              chart.tooltip.contentGenerator(params.contentGenerator);
            }
          }


          chart.xAxis.axisLabel(x_data.label).tickFormat(
            function(d){
              return String(d).toHHMMSS();
            }
          );

          chart.yAxis.axisLabel(y_data.label).axisLabelDistance(-18).tickFormat(
            function(d){
              if(d>1000000){return (d/1000000).toFixed(0) + "M";}
              else if(d>1000){return (d/1000).toFixed(0) + "K";}
              else { return d; }
            }
          );

          var chart_data = svg.datum(plot_data);
          chart_data.transition().duration(500).call(chart);
          return chart;
        }
      );


    });
  });

};


module.exports = {
  shard_lineup: shard_lineup,
  special_shard_lineup: special_shard_lineup,
  state_lineup: state_lineup,
  plot_shard_lineup: plot_shard_lineup,
  render_data: render_data,
};

},{"../ajax_cache":1,"../components":10,"../models":14,"../utils":20,"./tooltips.js":8}],7:[function(require,module,exports){
"use strict";
var utils = require("../utils");
var tooltips = require("./tooltips");
var Handlebars = window.Handlebars;
var $ = window.$;
var nv = window.nv;
var _ = window._;


var timeToSecs = function(time){
    return parseInt(time.split(":")[0])*60+parseInt(time.split(":")[1]);
};

var replay_lines = function(dataset, facet, destination, params){

  var x_label = toTitleCase("offset time");
  var y_label = toTitleCase(facet);
  if (params.label!==undefined) {
    var y_label = toTitleCase(params.label);
  }
  var data = dataset.map(function(series){
    var x = series.values.map(function(d){
         var t = new Date(1970, 0, 1); // Epoch
          t.setSeconds(d.offset_time);
        return t;
    })
    return {
      type: 'scattergl',
      x: x,
      y: series.values.map(function(d){return d[facet]}),
      name: series.shard.name
    }
  });

  var layout = {
    xaxis: {
      title: x_label,
      autotick: true,
      tickformat: '%H:%M:%S',
      nticks: 5,
    },
    yaxis: {
      title: y_label,
    },
    margin: {
      t: 20
    },
    hovermode: 'closest'
  };
  if(params.inset_legend){
    layout.legend = {
    x: 0.1,
    y: 1,
    traceorder: 'normal',
    font: {
      family: 'sans-serif',
      size: 12,
      color: '#FFF'
    },
    opacity: .5,
    borderwidth: 2
    }
  }

  $('.ajax-loader').remove();
  Plotly.newPlot(
    destination.substring(1,100),
    data,
    layout,
    { displaylogo: false,
      modeBarButtonsToRemove: ['sendDataToCloud'],
    }
  );
}

var stat_lineup = function(shards, facet, destination, params, log){

  if (log===undefined) {log = 'statelog';}

  if (log==='statelog') {
    var lookup_facet='allstate';
  }else{
    var lookup_facet=facet;
  }

  // Get the replay parse info
  Promise.all(
    shards.map(function(shard){
      var location = utils.parse_urls.url_for(shard, lookup_facet, log);
      return $.getJSON(location);
    })
  ).then(function(facets){
    var dataset = facets.map(function(dataseries, i){
      var myobj =  {
        'key': shards[i].name,
        'css_classes': shards[i].css_classes,
        'values': dataseries,
        'shard': shards[i]
      };
      return myobj;
    });
    replay_lines(dataset, facet, destination, params);
  }).catch(function(e){
    console.log(e);
  });
};


/**
 * Merges two data series that have the same periodicity but uneven starts.
 * @param {array} shardfacets - An array of 3-tuples: shard, facet, logtype.
 * @param {string} destination - Where to draw.
 * @param {integer} params - Adjustable stuffs.
 */
var multifacet_lineup = function(shardfacets, destination, params, label){

  // Get the replay parse info
  Promise.all(
    shardfacets.map(function(lst){
      if (lst[2]=='statelog') {
        var lookup_facet = 'allstate';
      }else{
        var lookup_facet = lst[1];
      }
      var location = utils.parse_urls.url_for(lst[0], lookup_facet, lst[2]);
      return $.getJSON(location);
    })
  ).then(function(facets){

    var dataset = facets.map(function(dataseries, i){

      var values = dataseries.map(function(d){
          d.value = d[shardfacets[i][1]]
          return d;
        });
      var myobj =  {
        'key': shardfacets[i][0].name + ' ' + shardfacets[i][1],
        'css_classes': shardfacets[i][0].css_classes,
        'values': values,
        'shard': shardfacets[i][0]
      };
      return myobj;
    });
    console.log(label);
    if (typeof label != 'undefined') {
      params.label = label;
    }
    replay_lines(dataset, 'value', destination, params);
  }).catch(function(e){
    console.log(e);
  });
};


/**
 * Merges two data series that have the same periodicity but uneven starts.
 * @param {array} data - The array of unevenly spaced series.
 * @param {string} facet - The named stat of the data samples to use.
 * @param {integer} stride - The spacing of the series (ex -10, 0, 10...) = 10.
 */
var scatterline_merge = function(data, facet, stride){

  var x = data[0];
  var y = data[1];

  var x0 = x[0];
  var x1 = x[x.length-1];
  var y0 = y[0];
  var y1 = y[y.length-1];

  var max_time = d3.max([x1.offset_time, y1.offset_time]);
  var min_time = d3.min([x0.offset_time, y0.offset_time]);



  var return_lst = [];

  for (var i = min_time; i <= max_time; i+=stride) {

    var x_val;
    if (i <= x0.offset_time) {
      x_val = x0[facet];
    }
    else if(i > x0.offset_time && i < x1.offset_time){
      // Ex 5, 10, 15, 20.  idx for 20 = (20-5)/5 = 3
      var series_idx = (i-x0.offset_time)/stride
      x_val = x[series_idx][facet];
    } else {
      x_val = x1[facet];
    }

    var y_val;
    if (i <= y0.offset_time) {
      y_val = y0[facet];
    }
    else if(i > y0.offset_time && i <= y1.offset_time){
      var series_idx = (i-y0.offset_time)/stride
      y_val = y[series_idx][facet];
    } else {
      y_val = y1[facet];
    }

    return_lst.push({
      offset_time: i,
      x: x_val,
      y: y_val,
    })
  };

  return return_lst;
}

var scatterline = function(shards, facet, destination, params, logtype){

  // Get the replay parse info
  Promise.all(
    shards.map(function(shard){
      var location = utils.parse_urls.url_for(shard, facet, logtype);
      return $.getJSON(location);
    })
  ).then(function(data){

    var width;
    var height;
    var start;
    var stop;
    var interpolation;
    var stride;
    var chart_destination = destination+" .chart";
    var label_destination = destination+" label";
    var x_label;
    var y_label;

    if(params!==undefined){

      if(params.start_time!==undefined&&params.start_time!==""){
        start = timeToSecs(params.start_time);
      } else {
        start = -10000;
      }

      if(params.end_time!==undefined&&params.end_time!==""){
        stop = timeToSecs(params.end_time);
      } else {
        stop = 10000;
      }

      if(params.x_label!==undefined){
        x_label = params.x_label;
      } else {
        x_label = 'X';
      }

      if(params.y_label!==undefined){
        y_label = params.y_label;
      } else {
        y_label = 'Y';
      }

      if(params.interpolation!==undefined){
        interpolation = params.interpolation;
      } else {
        interpolation = "step-after";
      }

      if(params.granularity!==undefined){
        stride = params.granularity;
      } else {
        stride = 10;
      }

    }

    // Trim down our data sets.
    var trimmed_data = data.map(function(d, i){
      var filtered_dataset = d.filter(function(x){
        return x.offset_time <= stop && x.offset_time >= start && x.offset_time.mod(stride) === 0;
      });
      return filtered_dataset;
    });

    var values = scatterline_merge(trimmed_data, facet, stride)

    // NVD3 freaks out and breaks tooltips if voronoi is false or dots overlap.
    var dumbhash = function(d){return d.x+"@@"+d.y}
    var dumbhashes = [];
    values = values.filter(function(a){
        if(dumbhashes.indexOf(dumbhash(a))<0){
          dumbhashes.push(dumbhash(a));
          return true;
        } else{
          return false;
        }
      });

    var plot_data = [{
      key: toTitleCase(facet),
      values: values
    }];

    $(chart_destination).empty();
    $(label_destination).html(toTitleCase(facet));

    var true_min = d3.min(trimmed_data, function(series){
      return d3.min(series, function(nested){
        return nested[facet];
      })
    });

    var true_max = d3.max(trimmed_data, function(series){
      return d3.max(series, function(nested){
        return nested[facet];
      })
    });


    var time_min = d3.min(trimmed_data, function(series){
      return d3.min(series, function(nested){
        return nested.offset_time;
      })
    });

    var time_max = d3.max(trimmed_data, function(series){
      return d3.max(series, function(nested){
        return nested.offset_time;
      })
    });


    var time_color = d3.scale.linear()
        .domain([
          -120, -1,
          0, 599,
          600, 1199,
          1200, 1799,
          1800, 2399,
          2400, 2999,
          3000, 3599,
          3600, 4199,
        ])
        .range([
          d3.rgb("black").brighter(.2), d3.rgb("black").darker(1.3),
          d3.rgb("red").brighter(.2), d3.rgb("red").darker(1.3),
          d3.rgb("orange").brighter(.2), d3.rgb("orange").darker(1.3),
          d3.rgb("yellow").brighter(.2), d3.rgb("yellow").darker(1.3),
          d3.rgb("green").brighter(.2), d3.rgb("green").darker(1.3),
          d3.rgb("blue").brighter(.2), d3.rgb("blue").darker(1.3),
          d3.rgb("violet").brighter(.2), d3.rgb("violet").darker(1.3),
          d3.rgb("gray").brighter(.2), d3.rgb("gray").darker(1.3),
        ]);

    var svg = utils.svg.square_svg(chart_destination, width, height);
    nv.addGraph(

      function(){
        var chart = nv.models.scatterChart()
          .margin({
            left: 50,
            bottom: 50,
          })
          .x(function(d){
            return d.x;
          })
          .y(function(d){
            return d.y;
          })
          .showLegend(false)
          .forceX([true_min, true_max])
          .forceY([true_min, true_max]);

        if(params !== undefined){

          if(params.height!==undefined){
            chart.height(params.height);
          }
          if(params.width!==undefined){
            chart.width(params.width);
          }
          if(params.forceY!==undefined){
            chart.forceY(params.forceY);
          }
          if(params.forceX!==undefined){
            chart.forceX(params.forceX);
          }
        }
        chart.tooltip.contentGenerator(
          tooltips.duel_tooltip_generator(x_label, y_label)
        );


        chart.xAxis.axisLabel(x_label)
          .tickFormat(utils.axis_format.pretty_numbers);

        chart.yAxis.axisLabel(y_label).axisLabelDistance(-15)
          .tickFormat(utils.axis_format.pretty_numbers);

        var chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      },
      function(){

        d3.selectAll('.nv-point')
            .style("fill", function(d){return time_color(d[0].offset_time)})
            .style('stroke', function(d){return time_color(d[0].offset_time)})
            .style('fill-opacity', 1)
      }
    );
  });
};


var counter = function(data, hasher){
    return data.map(hasher).reduce(function(prev, curr){
        if (!prev.hasOwnProperty(curr)) {
            prev[curr]=1;
        }
        else{
            prev[curr]+=1;
        }
        return prev;
    }, {});
}

var winnow = function(data, index){
  data[index] = data[data.length-1];
  data.pop();
  return data;
}

function findById(source, target_hash, hasher) {
  for (var i = 0; i < source.length; i++) {
    if (hasher(source[i]) === target_hash) {
      return i;
    }
  }
  throw "Couldn't find object with id: " + id;
}

/**
 * Merges two event series.
 * @param {array} data - The array of event series.
 * @param {string} hasher - Function for what to merge on.  Ex 'key' for items
 * @param {integer} null_time - Default to use lacking match
 */
var combat_merge = function(data, hasher, null_time){

  var x_data = data[0];
  var y_data = data[1];


  // Make the hashmaps for fast lookups.
  var x_counter = counter(x_data, hasher);
  var y_counter = counter(y_data, hasher);

  var return_lst = [];
  x_data.forEach(function(x){
    var hash = hasher(x);
    var return_obj = {
      'item': hash,
      'x': x.offset_time
    };
    if (y_counter[hash]>0) {

      var y_index = findById(y_data, hash, hasher);

      if(y_index===undefined) console.log('Freak');

      return_obj['y'] = y_data[y_index].offset_time;
      y_data.splice(y_index, 1);
      y_counter[hash]-=1;
    }else{
      return_obj['y'] = null_time;
    }

    return_lst.push(return_obj);
  })

  // None of these are in x
  y_data.forEach(function(y){
    var hash = hasher(y);
    var return_obj = {
      'item': hash,
      'y': y.offset_time,
      'x': null_time,
    };

    return_lst.push(return_obj);
  })

  return return_lst;
}

var item_scatter = function(shards, destination, params){

  var urls = shards.map(function(shard){
      var location = utils.parse_urls.url_for(shard, 'item_buys', 'combatlog');
      return $.getJSON(location);
    })
    urls.push($.getJSON('/rest-api/items/'))

  // Get the replay parse info
  Promise.all(
    urls
  ).then(function(data){

    var width;
    var height;
    var start;
    var stop;
    var interpolation;
    var stride;
    var chart_destination = destination+" .chart";
    var label_destination = destination+" label";
    var x_label;
    var y_label;

    if(params!==undefined){

      if(params.start_time!==undefined&&params.start_time!==""){
        start = timeToSecs(params.start_time);
      } else {
        start = -10000;
      }

      if(params.end_time!==undefined&&params.end_time!==""){
        stop = timeToSecs(params.end_time);
      } else {
        stop = 10000;
      }

      if(params.x_label!==undefined){
        x_label = params.x_label;
      } else {
        x_label = 'X';
      }

      if(params.y_label!==undefined){
        y_label = params.y_label;
      } else {
        y_label = 'Y';
      }

      if(params.interpolation!==undefined){
        interpolation = params.interpolation;
      } else {
        interpolation = "step-after";
      }

      if(params.granularity!==undefined){
        stride = params.granularity;
      } else {
        stride = 10;
      }

    }

    var cost_data = data.pop();
    var costs = cost_data.reduce(function(accu, item){
      accu[item.internal_name] = item.cost; return accu;
    }, {});
    // Trim down our data sets.
    var trimmed_data = data.map(function(d, i){
      var filtered_dataset = d.filter(function(x){
        return x.offset_time <= stop && x.offset_time >= start
      });
      return filtered_dataset;
    });

    var null_time = -300
    var values = combat_merge(
      trimmed_data, function(d){return d.key}, null_time
    );

    // NVD3 freaks out and breaks tooltips if voronoi is false or dots overlap.
    var dumbhash = function(d){return d.x+"@@"+d.y+"@@"+d.item}
    var dumbhashes = [];
    values = values.filter(function(a){
        if(dumbhashes.indexOf(dumbhash(a))<0){
          dumbhashes.push(dumbhash(a));
          return true;
        } else{
          return false;
        }
      });

    var plot_data = [{
      key: 'Item Buys',
      values: values
    }];


    var cost_radius = d3.scale.linear()
        .domain([
          0,
          500,
          1000,
          2000,
          3500,
          5000,
          6000,
          6999,
        ])
        .range([
          1,
          1.25,
          1.75,
          2,
          2.5,
          3,
          3.5,
          4,
        ]);


    values.map(function(d){
      var match = costs[d.item.substring(5)]
      if(match){
        d.cost = match;
      } else{
        d.cost = 0;
      }
      d.size = cost_radius(d.cost);
      return d
    })

    var cost_extent = d3.extent(plot_data[0].values, function(d){
      return d.cost;
    })

    var cost_color = d3.scale.linear()
        .domain([
          0, 499,
          500, 999,
          1000, 1999,
          2000, 3499,
          3500, 4999,
          5000, 5999,
          6000, 6999,
        ])
        .range([
          d3.rgb("black").brighter(.2), d3.rgb("black").darker(1.3),
          d3.rgb("red").brighter(.2), d3.rgb("red").darker(1.3),
          d3.rgb("orange").brighter(.2), d3.rgb("orange").darker(1.3),
          d3.rgb("yellow").brighter(.2), d3.rgb("yellow").darker(1.3),
          d3.rgb("green").brighter(.2), d3.rgb("green").darker(1.3),
          d3.rgb("blue").brighter(.2), d3.rgb("blue").darker(1.3),
          d3.rgb("violet").brighter(.2), d3.rgb("violet").darker(1.3),
        ]);

    $(chart_destination).empty();
    $(label_destination).html('Item Buys');

    var time_max = d3.max(trimmed_data, function(series){
      return d3.max(series, function(nested){
        return nested.offset_time;
      })
    });

    var svg = utils.svg.square_svg(chart_destination, width, height);
    nv.addGraph(

      function(){
        var chart = nv.models.scatterChart()
          .margin({
            left: 50,
            bottom: 50,
          })
          .x(function(d){
            return d.x;
          })
          .y(function(d){
            return d.y;
          })
          .showLegend(false)
          .forceX([null_time, time_max])
          .forceY([null_time, time_max]);

        if(params !== undefined){

          if(params.height!==undefined){
            chart.height(params.height);
          }
          if(params.width!==undefined){
            chart.width(params.width);
          }
          if(params.forceY!==undefined){
            chart.forceY(params.forceY);
          }
          if(params.forceX!==undefined){
            chart.forceX(params.forceX);
          }
        }
        chart.tooltip.contentGenerator(
          tooltips.duel_item_tooltip_generator(x_label, y_label)
        );


        chart.xAxis.axisLabel(x_label)
          .tickFormat(utils.axis_format.pretty_times);

        chart.yAxis.axisLabel(y_label).axisLabelDistance(-15)
          .tickFormat(utils.axis_format.pretty_times);

        var chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      },
      function(){
          d3.selectAll(destination+' .nv-point')
            .style("fill", function(d){return cost_color(d[0].cost)})
            .style('stroke', function(d){return cost_color(d[0].cost)})
            .style('stroke', function(d){return cost_color(d[0].cost)})
            .attr('r', function(d){return cost_radius(d[0].cost)})

      });
  });
};


var item_inventory = function(shards, destination, labels){

  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  })
  urls.push($.getJSON('/rest-api/items/'))
  // Get the replay parse info
  Promise.all(
    urls
  ).then(function(data){


    var cost_data = data.pop();
    var costs = cost_data.reduce(function(accu, item){
      accu[item.internal_name] = item.cost; return accu;
    }, {});
    // Trim down our data sets.

    var trimmed_data = data.map(function(series, i){
      var max = d3.max(series, function(d){return d.offset_time})
      var filtered_dataset = series.filter(function(x){
        return x.offset_time.mod(600) === 0 || x.offset_time == max;
      });
      return filtered_dataset;
    });

    var max_length = d3.max(trimmed_data, function(series){
      return series.length;
    });


    var prev_pms_time = -600;
    var table = '<table class="table  table-hover">';

    for (var time_idx=0; time_idx<max_length; time_idx++) {
      for(var series_idx = 0; series_idx<trimmed_data.length; series_idx++){


        var pms_label = labels[series_idx];
        var shard_id = shards[series_idx].id;
        var pms_time = trimmed_data[series_idx][time_idx].offset_time;

        table += '<tr class="inforow" data-shard-id="'+shard_id+'" data-min-time="'+prev_pms_time+'" data-max-time="'+pms_time+'">';

        table += '<td>'+pms_label+'</td>';

        if (trimmed_data[series_idx][time_idx]) {

          table += '<td>'+String(trimmed_data[series_idx][time_idx].offset_time).toHHMMSS()+'</td>';
        }else{

          table += '<td></td>';
        }
        var item_str = "";

        [
          'item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5'
        ].map(function(slot){
          var item;

          if (trimmed_data[series_idx][time_idx]) {
            item = trimmed_data[series_idx][time_idx][slot];
          }else{
            item = undefined;
          }

          if (item) {
            item_str+="<span><i class='d2items "+item.substring(5)+"'></i></span>"
          }else{
            item_str+="";
          }
        });

        table += '<td>'+item_str+'</td>';


        table += '</tr>';
      }
      table += '<tr class="spacer"><td></td><td></td><td></td></tr>';

      prev_pms_time = pms_time;

    }
    table += '</table>';
    $(destination+' #target').empty();
    $(destination+' #target').append(table);
    $(destination+' label').html('Inventory timings');
    $('.inforow').on('mouseover', function(){

      $(window).trigger('shardfilter', [
        $(this).data('shard-id'),
        $(this).data('min-time'),
        $(this).data('max-time'),
      ])
    });

  });
};

var minimap = function(shards, destination, params){

  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  })
  // Get the replay parse info
  Promise.all(urls).then(function(data){

    var css_class_swap = function(side){
      if (side === 'radiant') {
        return 'radiant-minimap-glow';
      }
      else if (side === 'dire') {
        return 'dire-minimap-glow';
      }
    }

    var position_data =  data.map(function(series, series_idx){
      return series.reduce(function(prev, d){
        prev[String(d.offset_time)] = {
          x: d.x,
          y: d.y,
          hero_name: shards[series_idx].hero_name,
          css_classes: css_class_swap(shards[series_idx].css_classes),
          minimap_label: shards[series_idx].minimap_label,
          health: d.health,
        }
        return prev;
      }, {})
    });

    var svg = make_map_background(destination)
    var width = svg.attr('width');
    var height = svg.attr('height');

    var fetch_data = position_data.map(function(d){
      return d[0]
    });

    var xscale = utils.axis_format.minimap_x(width, height);
    var yscale = utils.axis_format.minimap_y(width, height);

    var faces = d3.select(destination).selectAll('i').data(fetch_data)
      .enter()
      .append('i');

      faces.attr('class', function(d){
        return 'd2mh ' + d.hero_name + ' ' +d.css_classes;
      })
      .style('left', function(d){return xscale(d.x)+'px'})
      .style('top', function(d){return yscale(d.y)+'px'})
      .style('position', 'absolute')

      faces.append('span').attr('class', 'minimap-label').html(function(d){
        return d.minimap_label ? d.minimap_label : '';
      });


    $(window).on('update', function(evt, arg){
      var fetch_data = position_data.map(function(d){
        return d[arg]
      });

      var faces = d3.select(destination).selectAll('i').data(fetch_data);
      faces.classed('dead', function(d){
        if (d.health===0) {
          return true;
        }else{
          return false;
        }
      });

      faces
        .transition()
        .duration(1000)
        .style('left', function(d){
          if (d===undefined) {
            return xscale(0)+'px'
          }
          else{
            return xscale(d.x)+'px'
          }
        })
        .style('top', function(d){
          console.log(d, yscale(d.y))
          if (d===undefined) {
            return yscale(0)+'px'
          }else{
            var val = yscale(d.y) - 10;
            return val+'px'
          }
        }).ease("linear")

    })

  }).catch(function(e){
    console.log(e);
  })
};


var position_heatmap = function(shards, destination, params){
  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  })
  // Get the replay parse info
  Promise.all(urls).then(function(raw_data){

    $(destination+' .minimap-chart').empty();
    $(destination+' label').empty();
    $(destination+' .legend').empty();
    var svg = make_map_background(destination)
    var width = svg.attr('width');
    var height = svg.attr('height');

    var xscale = utils.axis_format.minimap_x(width, height);
    var yscale = utils.axis_format.minimap_y(width, height);

    var data = crosscount(raw_data[0]);

    var x_data = [1,5,10,30,60,120];
    var colors = d3.scale.linear()
    .domain(x_data)
    .range([
      d3.rgb("green"),
      d3.rgb("green").brighter(1),
      d3.rgb("orange"),
      d3.rgb("orange").brighter(1),
      d3.rgb("red"),
      d3.rgb("red").brighter(1),
    ]);

    var update_heat = function(data, label){
      var cards = svg.selectAll('.cell')
        .data(data,
          function(d) {return d.x+':'+d.y;}
        );

      cards.append("title");
      cards.select("title").text(function(d) { return d.ct; });

      var size = xscale(10)-xscale(9);

      cards.enter().append("rect")
          .attr("x", function(d) { return xscale(d.x)})
          .attr("y", function(d) { return yscale(d.y) })
          .attr("class", "cell")
          .attr("ddd-ct", function(d) { return d.ct })
          .attr("width", size+2)
          .attr("height", size+2)
          .style("fill", function(d){return colors(d.ct)})
          .style("stroke", function(d){return 'black'})
          .style("stroke-width", '1px')

      cards.transition().duration(1000)
          .style("fill", function(d) { return colors(d.ct); });


      cards.exit()
        .transition()
        .duration(1000)
        .style("opacity", 0)
        .remove();

      d3.select(destination+' label').html(label);
    }
    var get_label = function(shard, min_time, max_time){
      if (shard.label) {
        var prefix = shard.label;
      } else{
        var prefix = shard.name;
      }
      if(min_time!==undefined){
        return prefix+', '+String(min_time).toHHMMSS()+'-'+String(max_time).toHHMMSS()
      }else{
        return prefix+', all game'
      }
    }
    update_heat(data, get_label(shards[0]));




    var legend_data = x_data;
    var legend_width = $(destination).width();
    var legendElementWidth = legend_width/legend_data.length;
    var legend_height = legendElementWidth;

    var legend = d3.select(destination+' .legend')
      .append("svg")
      .attr("width", legend_width)
      .attr("height", legend_height);

    var selection = legend.selectAll('rect').data(legend_data).enter();

    selection.append("rect")
      .attr("x", function(d, i) { return legendElementWidth * i; })
      .attr("y", 0)
      .attr("width", legendElementWidth)
      .attr("height", legendElementWidth)
      .style("fill", function(d, i) {return colors(d); });


    selection.append("text")
      .attr("class", "legendtext")
      .text(function(d) {return "≥ " + Math.round(d)+'s'; })
      .attr("x", function(d, i) { return legendElementWidth * i+legendElementWidth/4; })
      .attr("y", legendElementWidth/2)
      .attr("fill", 'black');

    $(window).on('shardfilter', function(evt, id, min_time, max_time){
      var shard;
      var test = raw_data.filter(function(d, i){
        if (shards[i].id == id){
          shard = shards[i];
        }
        return shards[i].id == id;
      })[0].filter(function(d){
        return d.offset_time > min_time && d.offset_time <= max_time;
      });
      var updata = crosscount(test);
      update_heat(updata, get_label(shard, min_time, max_time));
    })


  }).catch(function(e){
    console.log(e);
  })

}

var make_map_background = function(destination){
    var svg = utils.svg.square_svg(destination+' .minimap-chart');
    var width = svg.attr('width');
    var height = svg.attr('height');

    var defs = svg.append('svg:defs');

    defs.append("svg:pattern")
        .attr("id", "minimap_img")
        .attr("width", width)
        .attr("height", height)
        .attr("patternUnits", "userSpaceOnUse")
        .append("svg:image")
        .attr("xlink:href", 'https://s3.amazonaws.com/datadrivendota/images/minimap.png')
        .attr("width", width)
        .attr("height", height)
        .attr("x", 0)
        .attr("y", 0);

    var rect = svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr("x", 0)
      .attr("y", 0)
      .attr('fill', "url(#minimap_img)");

    return svg;
}

var crosscount = function(series){
    var counts = {};
    series.map(function(point){
        if(!counts.hasOwnProperty(point.x)){
            counts[point.x] = {};
        }
        if(!counts[point.x].hasOwnProperty(point.y)){
            counts[point.x][point.y] = 0;
        }
        counts[point.x][point.y] += 1;
    });
    var answers = [];
    Object.getOwnPropertyNames(counts).map(function(idx){
        Object.getOwnPropertyNames(counts[idx]).map(function(idy){
            answers.push({
                x: parseInt(idx),
                y: parseInt(idy),
                ct: counts[idx][idy]
            });
        });
    });
    return answers;
}

var stat_card = function(shard, destination, params){

  var struct = {};
  var urls = [
    $.getJSON(utils.parse_urls.url_for(shard, 'allstate', 'statelog'))
  ];

  // Get the replay parse info
  Promise.all(urls).then(function(data){
    data = data[0];
    data.map(function(item){
      var time = item['offset_time'];
      struct[String(time)] = item;
    });

  }).then(function(items){
    var rawTemplate = `<div class="statcard {{css_classes}} {{lifestate}}">
    <div>
    <i class='d2mh {{hero_css}}'></i>
      <div style='float:right'>
      <div><text>{{kills}} / {{deaths}} / {{assists}}</text></div>
      <div><text>{{last_hits}} / {{denies}}</text></div>
      </div>
    </div>
          <div class="stats">
            <div class="css-progress-bar horizontal health">
              <div class="css-progress-track">
                <div class="css-progress-fill" style='width:{{health_pct}}%; float:left; background: green;'>
                  <span class='bar-nums'>{{health}} / {{max_health}}</span>
                </div>
              </div>
            </div>
            <div class='mana'>
            <div class="css-progress-bar horizontal mana">
              <div class="css-progress-track">
                <div class="css-progress-fill" style='width:{{mana_pct}}%; float:left; background: blue;'>
                  <span class='bar-nums'>{{mana}} / {{max_mana}}</span>
                </div>
              </div>
            </div>
           </div>
           <div class='strength'>
             Str: {{strength}} + {{strength_add}} = {{strength_total}}
           </div>
           <div class='intelligence'>
             Int: {{intelligence}} + {{intelligence_add}} = {{intelligence_total}}
           </div>
           <div class='agility'>
             Agi: {{agility}} + {{agility_add}} = {{agility_total}}
           </div>
           <div class='damage'>
             Dmg: {{base_damage}} + {{bonus_damage}} = {{total_damage}}
           </div>
           <div class='gold'>
             Gold: {{unreliable_gold}} + {{reliable_gold}} = {{total_gold}}
           </div>
           <div class='total_gold'>
             Tot Gold: {{total_earned_gold}}
           </div>
            <div class='row' id='items' style='text-align:center'>
              <div class='col-md-12'>
                <div class='row'>
                 <div class='col-xs-1' id='item_0'>
                    <i class='d2items {{item_0}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_1'>
                    <i class='d2items {{item_1}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_2'>
                    <i class='d2items {{item_2}}'></i>
                  </div>
                </div>
              </div>
              <div class='col-md-12'>
                <div class='row'>
                  <div class='col-xs-1' id='item_3'>
                    <i class='d2items {{item_3}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_4'>
                    <i class='d2items {{item_4}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_5'>
                    <i class='d2items {{item_5}}'></i>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>`;
    var compiledTemplate = Handlebars.compile(rawTemplate); // (step 2)
    // Items health mana kda last hits denies
    var update = function(time){

      var context = {
        title: shard.name,
        css_classes: shard.css_classes,
      };

      if (struct[time]===undefined) {
        $(destination).html('Not defined');
      }else{
        for (var attrname in struct[String(time)]) {
          context[attrname] = struct[String(time)][attrname];
        }
      }


      context['strength_add'] = (context['strength_total'] - context['strength']).toFixed(0);

      context['lifestate'] = context['health'] > 0 ? 'alive' : 'dead';



      context['health_pct'] = ((context['health'] / context['max_health'])*100).toFixed(0);
      context['mana_pct'] = ((context['mana'] / context['max_mana'])*100).toFixed(0);

      context['agility_add'] = (context['agility_total'] - context['agility']).toFixed(0);

      context['intelligence_add'] = (context['intelligence_total'] - context['intelligence']).toFixed(0);

      context['hero_css'] = shard.hero_name;

      context['total_gold'] = (
        parseInt(context['unreliable_gold']) + parseInt(context['reliable_gold'])
      ).toFixed(2);

      [
        'agility',
        'agility_total',
        'strength',
        'strength_total',
        'intelligence',
        'intelligence_total',
        'health',
        'max_health',
        'mana',
        'max_mana',
      ].map(function(field){
        context[field] = context[field].toFixed(0);
      });

      ['item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5'].map(
        function(d){
        if (context[d] === null) {
          context[d] = 'emptyitembg';
        }else{
          context[d] = context[d].substring(5);
        }
      });

      var html = compiledTemplate(context);
      $(destination).html(html);

    }

    update(0);
    $(window).on('update', function(evt, arg){
      update(arg);
    })

  }).catch(function(e){
    console.log(e);
  })
};


var playback_shards = function(shards){

  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  });
  var min;
  var max;
  var start = 0;

  // Get the replay parse info
  Promise.all(urls).then(function(data){
    min = d3.min(data, function(series){
      return d3.min(series, function(x){
        return x.offset_time
      })
    });
    max = d3.max(data, function(series){
      return d3.max(series, function(x){
        return x.offset_time
      })
    });
    window.jsUtils.playback(min, max, 1, utils.axis_format.pretty_times);
  }).catch(function(e){
    console.log(e);
  })




}

module.exports = {
  stat_lineup: stat_lineup,
  scatterline: scatterline,
  item_scatter: item_scatter,
  item_inventory: item_inventory,
  multifacet_lineup: multifacet_lineup,
  minimap: minimap,
  position_heatmap: position_heatmap,
  stat_card: stat_card,
  playback_shards: playback_shards
};

},{"../utils":20,"./tooltips":8}],8:[function(require,module,exports){
"use strict"
var d3 = window.d3;

var noformat_tooltip = function(x_var, y_var){
  var return_fn = function(d, x, y, z){
      if (d === null) {return "";}
      var series = d.series[0];
      d = d.point;
      var table = d3.select(document.createElement("table"));

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter0 = tbodyEnter
          .append("tr");

      trowEnter0.append("td")
            .classed("legend-color-guide",true)
            .append("div")
            .style("background-color", series.color);

      trowEnter0
          .append("td")
          .html(function(d){
            return toTitleCase(series.key);
          });


      var trowEnter1 = tbodyEnter
          .append("tr");

      trowEnter1
          .append("td")
          .html(toTitleCase(y_var)+": ");

      trowEnter1.append("td")
          .classed("value", true)
          .html(function(d){
            return d[y_var];
          });

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html(toTitleCase(x_var)+": ");

      if (x_var=='offset_time') {
        trowEnter2.append("td")
          .classed("value", true)
          .html(function(d){return String(d.offset_time).toHHMMSS()});
      }else{
        trowEnter2.append("td")
          .classed("value", true)
          .html(function(d){
            return d[y_var];
          });
      }



      var html = table.node().outerHTML;
      return html;
  }
  return return_fn;
};



var heroContentGenerator = function(getX, getY, xlab, ylab){
  var return_fn = function(d){
      if (d === null) {return "";}
      d = d[0];
      var table = d3.select(document.createElement("table"));

      // Make a header
      var theadEnter = table
          .selectAll("thead")
          .data([d])
          .enter()
          .append("thead");

      var trowEnter = theadEnter
          .append("tr");

      trowEnter.append("td")
      .html(function(p){
        return p.hero.name;
      });

      trowEnter
        .append("td")
        .append("i")
        .attr(
          "class",
          function(p){return "d2mh " + p.hero.internal_name;}
        );

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html(xlab+": ");

      trowEnter2.append("td")
          .classed("value", true)
          .html(function(p) {return getX(p)});


      var tBodyRowEnter = tbodyEnter.append("tr");

      tBodyRowEnter
          .append("td")
          .html(ylab+": ");

      tBodyRowEnter.append("td")
          .classed("value",true)
          .html(
            function(p, i) {
                return getY(p);
            }
          );

      tBodyRowEnter.selectAll("td").each(function(p) {
          if (p.highlight) {
              var opacityScale = d3.scale.linear()
              .domain([0,1])
              .range(["#fff", p.color]);

              var opacity = 0.6;
              d3.select(this)
                  .style("border-bottom-color", opacityScale(opacity))
                  .style("border-top-color", opacityScale(opacity))
              ;
          }
      });

      var html = table.node().outerHTML;
      if (d.footer !== undefined)
          html += "<div class='footer'>" + d.footer + "</div>";
      return html;

  };
  return return_fn;
};

var bldg_tooltip = function(d, x, y, z){
      if (d === null) {return "";}
      d = d.point;
      var table = d3.select(document.createElement("table"));

      var clean = function(str){
        if (str.slice(0,12)=="npc_dota_bad") {
            return str.replace("\_"," ").slice(17,99);
        } else {
            return str.replace("\_"," ").slice(18,99);
        }
      }

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter1 = tbodyEnter
          .append("tr");

      trowEnter1
          .append("td")
          .html("Bldg: ");

      trowEnter1.append("td")
          .classed("value", true)
          .html(function(x){
            return clean(x.key);
        });

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html("Time: ");

      trowEnter2.append("td")
          .classed("value", true)
          .html(function(x){return String(x.offset_time).toHHMMSS()});

      var trowEnter3 = tbodyEnter
          .append("tr");

      trowEnter3
          .append("td")
          .html("Killer: ");

      trowEnter3.append("td")
          .classed("value", true)
          .html(function(x){return x.unit.replace('npc_dota_hero_','').replace("_"," ");});


      var html = table.node().outerHTML;
      return html;

};

var item_tooltip = function(d, x, y, z){
      if (d === null) {return "";}
      d = d.point;
      var table = d3.select(document.createElement("table"));

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter1 = tbodyEnter
          .append("tr");

      trowEnter1
          .append("td")
          .html("Item: ");

      trowEnter1.append("td")
          .classed("value", true)
          .html(function(x){
            return x.key;
        });

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html("Time: ");

      trowEnter2.append("td")
          .classed("value", true)
          .html(function(x){return String(x.offset_time).toHHMMSS()});

      var trowEnter3 = tbodyEnter
          .append("tr");

      trowEnter3
          .append("td")
          .html("Hero: ");

      trowEnter3.append("td")
          .classed("value", true)
          .html(function(x){
            return x.unit.replace('npc_dota_hero_','').replace("_"," ");
          });


      var html = table.node().outerHTML;
      return html;

};

var match_tooltip = function(d, x, y, z){
      if (d === null) {return "";}
      d = d[0];

      var table = d3.select(document.createElement("table"));

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter1 = tbodyEnter
          .append("tr");

      trowEnter1
          .append("td")
          .html("Match ID: ");

      trowEnter1.append("td")
          .html(function(x){
            return x.steam_id;
        });

      var trowEnter2 = tbodyEnter
          .append("tr");


      trowEnter2.append("td")
          .html('Teams');

      trowEnter2.append("td")
          .html(function(x){
            return x.radiant_team + ' vs. ' + x.dire_team
          });


      var html = table.node().outerHTML;
      return html;

};

var duel_tooltip_generator = function(x_name, y_name){

    var duel_tooltip = function(d, x, y, z){
          if (d === null) {return "";}
          d = d.point;

          var table = d3.select(document.createElement("table"));

          // Make a body
          var tbodyEnter = table
              .selectAll("tbody")
              .data([d])
              .enter()
              .append("tbody");

          var trowEnter1 = tbodyEnter
              .append("tr");

          trowEnter1
              .append("td")
              .html("Match Time: ");

          trowEnter1.append("td")
              .html(function(x){
                return String(x.offset_time).toHHMMSS();
            });

          var trowEnter2 = tbodyEnter
              .append("tr");

          trowEnter2.append("td")
              .html(x_name);

          trowEnter2.append("td")
              .html(function(x){
                return x.x
              });

          var trowEnter3 = tbodyEnter
              .append("tr");

          trowEnter3.append("td")
              .html(y_name);

          trowEnter3.append("td")
              .html(function(x){
                return x.y
              });


          var html = table.node().outerHTML;
          return html;

    };

return duel_tooltip;

};


var duel_item_tooltip_generator = function(x_name, y_name){

    var duel_tooltip = function(d, x, y, z){
          if (d === null) {return "";}
          d = d.point;

          var table = d3.select(document.createElement("table"));

          // Make a body
          var tbodyEnter = table
              .selectAll("tbody")
              .data([d])
              .enter()
              .append("tbody");

          var trowEnter0 = tbodyEnter
              .append("tr");

          trowEnter0
              .append("td")
              .html("Item: ");

          trowEnter0.append("td")
              .html(function(x){
                return toTitleCase(x.item.substring(5));
            });

          var trowEnter2 = tbodyEnter
              .append("tr");

          trowEnter2.append("td")
              .html(x_name);

          trowEnter2.append("td")
              .html(function(x){
                return String(x.x).toHHMMSS()
              });

          var trowEnter3 = tbodyEnter
              .append("tr");

          trowEnter3.append("td")
              .html(y_name);

          trowEnter3.append("td")
              .html(function(x){
                return String(x.y).toHHMMSS()
              });

          var trowEnter3 = tbodyEnter
              .append("tr");

          trowEnter3.append("td")
              .html('(Cost)');

          trowEnter3.append("td")
              .html(function(x){
                return String(x.cost)
              });


          var html = table.node().outerHTML;
          return html;

    };

return duel_tooltip;

};


module.exports = {
    hero_tooltip: heroContentGenerator,
    bldg_tooltip: bldg_tooltip,
    item_tooltip: item_tooltip,
    match_tooltip: match_tooltip,
    duel_tooltip_generator: duel_tooltip_generator,
    duel_item_tooltip_generator: duel_item_tooltip_generator,
    noformat_tooltip: noformat_tooltip
};

},{}],9:[function(require,module,exports){
var offset_time = {
    label: "Minutes from Horn",
    access: function(d){
        return d.offset_time;
    }
};

var sum = {
  label: "Total",
  access: function(d){return d.sum;}
};

module.exports = {
    sum: sum,
    offset_time: offset_time,
}

},{}],10:[function(require,module,exports){
'use strict';
var axes = require('./axes.js');

module.exports = {
    axes: axes,
};

},{"./axes.js":9}],11:[function(require,module,exports){
'use strict';

var nvd3 = window.nv;

nvd3.extensions = {};
nvd3.extensions.charts = require('./charts');
nvd3.extensions.utils = require('./utils');
nvd3.extensions.models = require('./models');
nvd3.extensions.components = require('./components');


module.exports = nvd3;

},{"./charts":4,"./components":10,"./models":14,"./utils":20}],12:[function(require,module,exports){
//TODO: consider deprecating by adding necessary features to multiBar model
var discreteBar = function() {
    "use strict";

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var margin = {top: 0, right: 0, bottom: 0, left: 0}
        , width = 960
        , height = 500
        , id = Math.floor(Math.random() * 10000) //Create semi-unique ID in case user doesn't select one
        , container
        , x = d3.scale.ordinal()
        , y = d3.scale.linear()
        , getX = function(d) { return d.x }
        , getY = function(d) { return d.y }
        , forceY = [0] // 0 is forced by default.. this makes sense for the majority of bar graphs... user can always do chart.forceY([]) to remove
        , color = nv.utils.defaultColor()
        , showValues = false
        , valueFormat = d3.format(',.2f')
        , xDomain
        , yDomain
        , xRange
        , yRange
        , dispatch = d3.dispatch('chartClick', 'elementClick', 'elementDblClick', 'elementMouseover', 'elementMouseout', 'elementMousemove', 'renderEnd')
        , rectClass = 'discreteBar'
        , duration = 250
        ;

    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var x0, y0;
    var renderWatch = nv.utils.renderWatch(dispatch, duration);

    function chart(selection) {
        renderWatch.reset();
        selection.each(function(data) {
            var availableWidth = width - margin.left - margin.right,
                availableHeight = height - margin.top - margin.bottom;

            container = d3.select(this);
            nv.utils.initSVG(container);

            //add series index to each data point for reference
            data.forEach(function(series, i) {
                series.values.forEach(function(point) {
                    point.series = i;
                });
            });

            // Setup Scales
            // remap and flatten the data for use in calculating the scales' domains
            var seriesData = (xDomain && yDomain) ? [] : // if we know xDomain and yDomain, no need to calculate
                data.map(function(d) {
                    return d.values.map(function(d,i) {
                        return { x: getX(d,i), y: getY(d,i), y0: d.y0 }
                    })
                });

            x   .domain(xDomain || d3.merge(seriesData).map(function(d) { return d.x }))
                .rangeBands(xRange || [0, availableWidth], .1);
            y   .domain(yDomain || d3.extent(d3.merge(seriesData).map(function(d) { return d.y }).concat(forceY)));

            // If showValues, pad the Y axis range to account for label height
            if (showValues) y.range(yRange || [availableHeight - (y.domain()[0] < 0 ? 12 : 0), y.domain()[1] > 0 ? 12 : 0]);
            else y.range(yRange || [availableHeight, 0]);

            //store old scales if they exist
            x0 = x0 || x;
            y0 = y0 || y.copy().range([y(0),y(0)]);

            // Setup containers and skeleton of chart
            var wrap = container.selectAll('g.nv-wrap.nv-discretebar').data([data]);
            var wrapEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-discretebar');
            var gEnter = wrapEnter.append('g');
            var g = wrap.select('g');

            gEnter.append('g').attr('class', 'nv-groups');
            wrap.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            //TODO: by definition, the discrete bar should not have multiple groups, will modify/remove later
            var groups = wrap.select('.nv-groups').selectAll('.nv-group')
                .data(function(d) { return d }, function(d) { return d.key });
            groups.enter().append('g')
                .style('stroke-opacity', 1e-6)
                .style('fill-opacity', 1e-6);
            groups.exit()
                .watchTransition(renderWatch, 'discreteBar: exit groups')
                .style('stroke-opacity', 1e-6)
                .style('fill-opacity', 1e-6)
                .remove();
            groups
                .attr('class', function(d,i) { return 'nv-group nv-series-' + i })
                .classed('hover', function(d) { return d.hover });
            groups
                .watchTransition(renderWatch, 'discreteBar: groups')
                .style('stroke-opacity', 1)
                .style('fill-opacity', .75);

            var bars = groups.selectAll('g.nv-bar')
                .data(function(d) { return d.values });
            bars.exit().remove();

            var barsEnter = bars.enter().append('g')
                .attr('transform', function(d,i,j) {
                    return 'translate(' + (x(getX(d,i)) + x.rangeBand() * .05 ) + ', ' + y(0) + ')'
                })
                .on('mouseover', function(d,i) { //TODO: figure out why j works above, but not here
                    d3.select(this).classed('hover', true);
                    dispatch.elementMouseover({
                        data: d,
                        index: i,
                        color: d3.select(this).style("fill")
                    });
                })
                .on('mouseout', function(d,i) {
                    d3.select(this).classed('hover', false);
                    dispatch.elementMouseout({
                        data: d,
                        index: i,
                        color: d3.select(this).style("fill")
                    });
                })
                .on('mousemove', function(d,i) {
                    dispatch.elementMousemove({
                        data: d,
                        index: i,
                        color: d3.select(this).style("fill")
                    });
                })
                .on('click', function(d,i) {
                    dispatch.elementClick({
                        data: d,
                        index: i,
                        color: d3.select(this).style("fill")
                    });
                    d3.event.stopPropagation();
                })
                .on('dblclick', function(d,i) {
                    dispatch.elementDblClick({
                        data: d,
                        index: i,
                        color: d3.select(this).style("fill")
                    });
                    d3.event.stopPropagation();
                });

            barsEnter.append('rect')
                .attr('height', 0)
                .attr('width', x.rangeBand() * .9 / data.length )

            if (showValues) {
                barsEnter.append('text')
                    .attr('text-anchor', 'middle')
                ;

                bars.select('text')
                    .text(function(d,i) { return valueFormat(getY(d,i)) })
                    .watchTransition(renderWatch, 'discreteBar: bars text')
                    .attr('x', x.rangeBand() * .9 / 2)
                    .attr('y', function(d,i) { return getY(d,i) < 0 ? y(getY(d,i)) - y(0) + 12 : -4 })

                ;
            } else {
                bars.selectAll('text').remove();
            }

            bars
                .attr('class', function(d,i) { return getY(d,i) < 0 ? 'nv-bar negative' : 'nv-bar positive' })
                .style('fill', function(d,i) { return d.color || color(d,i) })
                .style('stroke', function(d,i) { return d.color || color(d,i) })
                .select('rect')
                .attr('class', function(d){
                    return rectClass+' foo';
                })
                .watchTransition(renderWatch, 'discreteBar: bars rect')
                .attr('width', x.rangeBand() * .9 / data.length);
            bars.watchTransition(renderWatch, 'discreteBar: bars')
                //.delay(function(d,i) { return i * 1200 / data[0].values.length })
                .attr('transform', function(d,i) {
                    var left = x(getX(d,i)) + x.rangeBand() * .05,
                        top = getY(d,i) < 0 ?
                            y(0) :
                                y(0) - y(getY(d,i)) < 1 ?
                            y(0) - 1 : //make 1 px positive bars show up above y=0
                            y(getY(d,i));

                    return 'translate(' + left + ', ' + top + ')'
                })
                .select('rect')
                .attr('height', function(d,i) {
                    return  Math.max(Math.abs(y(getY(d,i)) - y((yDomain && yDomain[0]) || 0)) || 1)
                });


            //store old scales for use in transitions on update
            x0 = x.copy();
            y0 = y.copy();

        });

        renderWatch.renderEnd('discreteBar immediate');
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    chart.dispatch = dispatch;
    chart.options = nv.utils.optionsFunc.bind(chart);

    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        width:   {get: function(){return width;}, set: function(_){width=_;}},
        height:  {get: function(){return height;}, set: function(_){height=_;}},
        forceY:  {get: function(){return forceY;}, set: function(_){forceY=_;}},
        showValues: {get: function(){return showValues;}, set: function(_){showValues=_;}},
        x:       {get: function(){return getX;}, set: function(_){getX=_;}},
        y:       {get: function(){return getY;}, set: function(_){getY=_;}},
        xScale:  {get: function(){return x;}, set: function(_){x=_;}},
        yScale:  {get: function(){return y;}, set: function(_){y=_;}},
        xDomain: {get: function(){return xDomain;}, set: function(_){xDomain=_;}},
        yDomain: {get: function(){return yDomain;}, set: function(_){yDomain=_;}},
        xRange:  {get: function(){return xRange;}, set: function(_){xRange=_;}},
        yRange:  {get: function(){return yRange;}, set: function(_){yRange=_;}},
        valueFormat:    {get: function(){return valueFormat;}, set: function(_){valueFormat=_;}},
        id:          {get: function(){return id;}, set: function(_){id=_;}},
        rectClass: {get: function(){return rectClass;}, set: function(_){rectClass=_;}},

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = _.top    !== undefined ? _.top    : margin.top;
            margin.right  = _.right  !== undefined ? _.right  : margin.right;
            margin.bottom = _.bottom !== undefined ? _.bottom : margin.bottom;
            margin.left   = _.left   !== undefined ? _.left   : margin.left;
        }},
        color:  {get: function(){return color;}, set: function(_){
            color = nv.utils.getColor(_);
        }},
        duration: {get: function(){return duration;}, set: function(_){
            duration = _;
            renderWatch.reset(duration);
        }}
    });

    nv.utils.initOptions(chart);

    return chart;
};
module.exports = {
    discrete_bar: discreteBar
}

},{}],13:[function(require,module,exports){

var discreteBarChart = function() {
    "use strict";

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var discretebar = nv.models.discreteBar()
        , xAxis = nv.models.axis()
        , yAxis = nv.models.axis()
        , tooltip = nv.models.tooltip()
        ;

    var margin = {top: 15, right: 10, bottom: 50, left: 60}
        , width = null
        , height = null
        , color = nv.utils.getColor()
        , showXAxis = true
        , showYAxis = true
        , rightAlignYAxis = false
        , staggerLabels = false
        , x
        , y
        , noData = null
        , dispatch = d3.dispatch('beforeUpdate','renderEnd')
        , duration = 250
        ;

    xAxis
        .orient('bottom')
        .showMaxMin(false)
        .tickFormat(function(d) { return d })
    ;
    yAxis
        .orient((rightAlignYAxis) ? 'right' : 'left')
        .tickFormat(d3.format(',.1f'))
    ;

    tooltip
        .duration(0)
        .headerEnabled(false)
        .valueFormatter(function(d, i) {
            return yAxis.tickFormat()(d, i);
        })
        .keyFormatter(function(d, i) {
            return xAxis.tickFormat()(d, i);
        });

    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var renderWatch = nv.utils.renderWatch(dispatch, duration);

    function chart(selection) {
        renderWatch.reset();
        renderWatch.models(discretebar);
        if (showXAxis) renderWatch.models(xAxis);
        if (showYAxis) renderWatch.models(yAxis);

        selection.each(function(data) {
            var container = d3.select(this),
                that = this;
            nv.utils.initSVG(container);
            var availableWidth = nv.utils.availableWidth(width, container, margin),
                availableHeight = nv.utils.availableHeight(height, container, margin);

            chart.update = function() {
                dispatch.beforeUpdate();
                container.transition().duration(duration).call(chart);
            };
            chart.container = this;

            // Display No Data message if there's nothing to show.
            if (!data || !data.length || !data.filter(function(d) { return d.values.length }).length) {
                nv.utils.noData(chart, container);
                return chart;
            } else {
                container.selectAll('.nv-noData').remove();
            }

            // Setup Scales
            x = discretebar.xScale();
            y = discretebar.yScale().clamp(true);

            // Setup containers and skeleton of chart
            var wrap = container.selectAll('g.nv-wrap.nv-discreteBarWithAxes').data([data]);
            var gEnter = wrap.enter().append('g').attr('class', 'nvd3 nv-wrap nv-discreteBarWithAxes').append('g');
            var defsEnter = gEnter.append('defs');
            var g = wrap.select('g');

            gEnter.append('g').attr('class', 'nv-x nv-axis');
            gEnter.append('g').attr('class', 'nv-y nv-axis')
                .append('g').attr('class', 'nv-zeroLine')
                .append('line');

            gEnter.append('g').attr('class', 'nv-barsWrap');

            g.attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

            if (rightAlignYAxis) {
                g.select(".nv-y.nv-axis")
                    .attr("transform", "translate(" + availableWidth + ",0)");
            }

            // Main Chart Component(s)
            discretebar
                .width(availableWidth)
                .height(availableHeight);

            var barsWrap = g.select('.nv-barsWrap')
                .datum(data.filter(function(d) { return !d.disabled }));

            barsWrap.transition().call(discretebar);


            defsEnter.append('clipPath')
                .attr('id', 'nv-x-label-clip-' + discretebar.id())
                .append('rect');

            g.select('#nv-x-label-clip-' + discretebar.id() + ' rect')
                .attr('width', x.rangeBand() * (staggerLabels ? 2 : 1))
                .attr('height', 16)
                .attr('x', -x.rangeBand() / (staggerLabels ? 1 : 2 ));

            // Setup Axes
            if (showXAxis) {
                xAxis
                    .scale(x)
                    ._ticks( nv.utils.calcTicksX(availableWidth/100, data) )
                    .tickSize(-availableHeight, 0);

                g.select('.nv-x.nv-axis')
                    .attr('transform', 'translate(0,' + (y.range()[0] + ((discretebar.showValues() && y.domain()[0] < 0) ? 16 : 0)) + ')');
                g.select('.nv-x.nv-axis').call(xAxis);

                var xTicks = g.select('.nv-x.nv-axis').selectAll('g');
                if (staggerLabels) {
                    xTicks
                        .selectAll('text')
                        .attr('transform', function(d,i,j) { return 'translate(0,' + (j % 2 == 0 ? '5' : '17') + ')' })
                }
            }

            if (showYAxis) {
                yAxis
                    .scale(y)
                    ._ticks( nv.utils.calcTicksY(availableHeight/36, data) )
                    .tickSize( -availableWidth, 0);

                g.select('.nv-y.nv-axis').call(yAxis);
            }

            // Zero line
            g.select(".nv-zeroLine line")
                .attr("x1",0)
                .attr("x2",availableWidth)
                .attr("y1", y(0))
                .attr("y2", y(0))
            ;
        });

        renderWatch.renderEnd('discreteBar chart immediate');
        return chart;
    }

    //============================================================
    // Event Handling/Dispatching (out of chart's scope)
    //------------------------------------------------------------

    discretebar.dispatch.on('elementMouseover.tooltip', function(evt) {
        evt['series'] = {
            key: chart.x()(evt.data),
            value: chart.y()(evt.data),
            color: evt.color
        };
        tooltip.data(evt).hidden(false);
    });

    discretebar.dispatch.on('elementMouseout.tooltip', function(evt) {
        tooltip.hidden(true);
    });

    discretebar.dispatch.on('elementMousemove.tooltip', function(evt) {
        tooltip.position({top: d3.event.pageY, left: d3.event.pageX})();
    });

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    chart.dispatch = dispatch;
    chart.discretebar = discretebar;
    chart.xAxis = xAxis;
    chart.yAxis = yAxis;
    chart.tooltip = tooltip;

    chart.options = nv.utils.optionsFunc.bind(chart);

    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        width:      {get: function(){return width;}, set: function(_){width=_;}},
        height:     {get: function(){return height;}, set: function(_){height=_;}},
        staggerLabels: {get: function(){return staggerLabels;}, set: function(_){staggerLabels=_;}},
        showXAxis: {get: function(){return showXAxis;}, set: function(_){showXAxis=_;}},
        showYAxis: {get: function(){return showYAxis;}, set: function(_){showYAxis=_;}},
        noData:    {get: function(){return noData;}, set: function(_){noData=_;}},

        // deprecated options
        tooltips:    {get: function(){return tooltip.enabled();}, set: function(_){
            // deprecated after 1.7.1
            nv.deprecated('tooltips', 'use chart.tooltip.enabled() instead');
            tooltip.enabled(!!_);
        }},
        tooltipContent:    {get: function(){return tooltip.contentGenerator();}, set: function(_){
            // deprecated after 1.7.1
            nv.deprecated('tooltipContent', 'use chart.tooltip.contentGenerator() instead');
            tooltip.contentGenerator(_);
        }},

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = _.top    !== undefined ? _.top    : margin.top;
            margin.right  = _.right  !== undefined ? _.right  : margin.right;
            margin.bottom = _.bottom !== undefined ? _.bottom : margin.bottom;
            margin.left   = _.left   !== undefined ? _.left   : margin.left;
        }},
        duration: {get: function(){return duration;}, set: function(_){
            duration = _;
            renderWatch.reset(duration);
            discretebar.duration(duration);
            xAxis.duration(duration);
            yAxis.duration(duration);
        }},
        color:  {get: function(){return color;}, set: function(_){
            color = nv.utils.getColor(_);
            discretebar.color(color);
        }},
        rightAlignYAxis: {get: function(){return rightAlignYAxis;}, set: function(_){
            rightAlignYAxis = _;
            yAxis.orient( (_) ? 'right' : 'left');
        }}
    });

    nv.utils.inheritOptions(chart, discretebar);
    nv.utils.initOptions(chart);

    return chart;
}
module.exports = {
    discrete_bar_chart: discreteBarChart
}

},{}],14:[function(require,module,exports){
'use strict';
var scatter = require('./scatter.js').scatter;
var scatter_chart = require('./scatter_chart.js').scatter_chart;
var discrete_bar = require('./discrete_bar.js').discrete_bar;
var discrete_bar_chart = require('./discrete_bar_chart.js').discrete_bar_chart;

module.exports = {
    scatter: scatter,
    scatter_chart: scatter_chart,
    discrete_bar: discrete_bar,
    discrete_bar_chart: discrete_bar_chart,
};

},{"./discrete_bar.js":12,"./discrete_bar_chart.js":13,"./scatter.js":15,"./scatter_chart.js":16}],15:[function(require,module,exports){
'use strict';
var d3 = window.d3;
var utils = require('../utils');

var scatter = function() {

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    // Config
    var margin       = {top: 0, right: 0, bottom: 0, left: 0};
    var width        = null;
    var height       = null;
    var color        = nv.utils.defaultColor();  // chooses color
    var id           = Math.floor(Math.random() * 100000);  // Create semi-unique ID incase user doesn't select one
    var container    = null;

    // Scales
    var x = d3.scale.linear();
    var y = d3.scale.linear();
    var z = d3.scale.linear(); //linear b/c d3.svg.shape.size is treated as area


    // Accessors to data
    var getX         = function(d) { return d.x; };
    var getY         = function(d) { return d.y; };
    var getSize      = function(d) { return d.size || 1; };
    var getShape     = function(d) { return d.shape || 'circle'; };

    // Interactivity config
    var interactive  = true; // If true, plots a voronoi overlay for advanced point intersection
    var pointActive  = function(d) { return !d.notActive }; // any points that return false will be filtered out
    var padData      = false; // If true, adds half a data points width to front and back, for lining up a line chart with a bar chart
    var padDataOuter = .1; //outerPadding to imitate ordinal scale outer padding
    var clipEdge     = false; // if true, masks points within x and y scale
    var clipVoronoi  = true; // if true, masks each point with a circle... can turn off to slightly increase performance
    var showVoronoi  = false; // display the voronoi areas
    var clipRadius   = function() { return 25 }; // function to get the radius for voronoi point clips

    // Overrides
    var xDomain      = null;
    var yDomain      = null;
    var xRange       = null;
    var yRange       = null;
    var sizeDomain   = null; // Override point size domain
    var forceX       = []; // (ie. 0, or a max / min, etc.)
    var forceY       = [];
    var forceSize    = [];

    var sizeRange    = null;
    var singlePoint  = false;
    var dispatch     = d3.dispatch(
        'elementClick',
        'elementDblClick',
        'elementMouseover',
        'elementMouseout',
        'renderEnd'
    );
    var useVoronoi   = true;
    var duration     = 250;


    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var timeoutID
    var needsUpdate = false // Flag for when the points are visually updating, but the interactive layer is behind, to disable tooltips
    var renderWatch = nv.utils.renderWatch(dispatch, duration)
    var _sizeRange_def = [16, 256]
        ;

    var chart = function(selection) {
        renderWatch.reset();
        selection.each(function(data) {
            container = d3.select(this);
            var availableWidth = nv.utils.availableWidth(
                width, container, margin
            );
            var availableHeight = nv.utils.availableHeight(
                height, container, margin
            );

            nv.utils.initSVG(container);

            //add series index to each data point for reference
            data.forEach(function(series, i) {
                series.values.forEach(function(point) {
                    point.series = i;
                });
            });

            // Setup Scales
            // remap and flatten the data for use in calculating the scales' domains
            var seriesData = (xDomain && yDomain && sizeDomain) ? [] : // if we know xDomain and yDomain and sizeDomain, no need to calculate.... if Size is constant remember to set sizeDomain to speed up performance
                d3.merge(
                    data.map(function(d) {
                        return d.values.map(function(d,i) {
                            return {x: getX(d), y: getY(d), size: getSize(d)};
                        });
                    })
                );

            x.domain(
                xDomain || d3.extent(
                    seriesData.map(function(d) { return d.x; }).concat(forceX)
                )
            );

            if (padData && data[0])
                x.range(xRange || [(availableWidth * padDataOuter +  availableWidth) / (2 *data[0].values.length), availableWidth - availableWidth * (1 + padDataOuter) / (2 * data[0].values.length)  ]);
            //x.range([availableWidth * .5 / data[0].values.length, availableWidth * (data[0].values.length - .5)  / data[0].values.length ]);
            else
                x.range(xRange || [0, availableWidth]);

            y.domain(
                yDomain || d3.extent(
                    seriesData.map(function(d) { return d.y; }).concat(forceY)
                )
            ).range(yRange || [availableHeight, 0]);

            z.domain(
                sizeDomain || d3.extent(
                    seriesData.map(function(d) { return d.size; }).concat(forceSize)
                    )
                ).range(sizeRange || _sizeRange_def);

            // If scale's domain don't have a range, slightly adjust to make one... so a chart can show a single data point
            singlePoint = x.domain()[0] === x.domain()[1] || y.domain()[0] === y.domain()[1];

            if (x.domain()[0] === x.domain()[1])
                x.domain()[0] ?
                    x.domain([x.domain()[0] - x.domain()[0] * 0.01, x.domain()[1] + x.domain()[1] * 0.01])
                    : x.domain([-1,1]);

            if (y.domain()[0] === y.domain()[1])
                y.domain()[0] ?
                    y.domain([y.domain()[0] - y.domain()[0] * 0.01, y.domain()[1] + y.domain()[1] * 0.01])
                    : y.domain([-1,1]);

            if ( isNaN(x.domain()[0])) {
                x.domain([-1,1]);
            }

            if ( isNaN(y.domain()[0])) {
                y.domain([-1,1]);
            }


            // Setup containers and skeleton of chart
            var wrap = container.selectAll('g.nv-wrap.nv-scatter').data([data]);

            var wrapEnter = wrap.enter().append('g').attr(
                'class', 'nvd3 nv-wrap nv-scatter nv-chart-' + id
            );

            var defsEnter = wrapEnter.append('defs');
            var gEnter = wrapEnter.append('g');
            var g = wrap.select('g');

            wrap.classed('nv-single-point', singlePoint);
            gEnter.append('g').attr('class', 'nv-groups');
            gEnter.append('g').attr('class', 'nv-point-paths');
            wrapEnter.append('g').attr('class', 'nv-point-clips');

            wrap.attr(
                'transform',
                'translate(' + margin.left + ',' + margin.top + ')'
            );

            defsEnter.append('clipPath')
                .attr('id', 'nv-edge-clip-' + id)
                .append('rect');

            wrap.select('#nv-edge-clip-' + id + ' rect')
                .attr('width', availableWidth)
                .attr('height', (availableHeight > 0) ? availableHeight : 0);

            g.attr(
                'clip-path', clipEdge ? 'url(#nv-edge-clip-' + id + ')' : ''
            );

            needsUpdate = true;


            // Create groups
            var groups = wrap.select('.nv-groups').selectAll('.nv-group')
                .data(
                    function(d) { return d; },
                    function(d) { return d.key; }
                );

            groups.enter().append('g')
                .style('stroke-opacity', 1e-6)
                .style('fill-opacity', 1e-6);

            groups
                .exit()
                .remove();

            groups
                .attr(
                    'class',
                    function(d,i) { return 'nv-group nv-series-' + i; }
                )
                .classed('hover', function(d) { return d.hover; });

            groups.watchTransition(renderWatch, 'scatter: groups')
                .style('fill', function(d,i) { return color(d, i); })
                .style('stroke', function(d,i) { return color(d, i); })
                .style('stroke-opacity', 1)
                .style('fill-opacity', 0.5);


            // create points, maintaining their IDs from the original data set
            var points = groups.selectAll('circle.nv-point')
                .data(function(d) {
                    return d.values.map(
                        function (point, pointIndex) {
                            return [point, pointIndex];
                        }).filter(
                            function(pointArray, pointIndex) {
                                return pointActive(pointArray[0], pointIndex);
                            });
                    });

            points
                .enter()
                .append('circle')
                .attr('cx', function(d){return x(getX(d[0])).toFixed(2);})
                .attr('cy', function(d){return y(getY(d[0])).toFixed(2);})
                .attr('r', function(d){return 5;});

            points.each(function(d) {
                d3.select(this)
                    .classed('nv-point', true)
                    .classed('nv-point-doctor', true)
                    .classed('nv-point-' + d[1], true)
                    .classed('nv-noninteractive', !interactive)
                    .classed('hover', false)
                ;
            });

            points
                .watchTransition(renderWatch, 'scatter points')
                .attr('cx', function(d){ return x(getX(d[0]));})
                .attr('cy', function(d){ return y(getY(d[0]));});


            // Handle exits
            points
                .exit()
                .remove();

            groups
                .exit()
                .selectAll('circle.nv-point')
                .watchTransition(renderWatch, 'scatter exit')
                .attr(
                    'transform',
                    function(d) {
                        return 'translate(' + x(getX(d[0])) + ',' + y(getY(d[0])) + ')';
                })
                .remove();

        });
        renderWatch.renderEnd('scatter immediate');
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    chart.dispatch = dispatch;
    chart.options = nv.utils.optionsFunc.bind(chart);

    // utility function calls provided by this chart
    chart._calls = {
        clearHighlights: function () {
            nv.dom.write(function() {
                container.selectAll('.nv-point.hover').classed('hover', false);
            });
            return null;
        },
        highlightPoint: function (seriesIndex, pointIndex, isHoverOver) {
            nv.dom.write(function() {
                container.select('.nv-groups')
                  .selectAll('.nv-series-' + seriesIndex)
                  .selectAll('.nv-point-' + pointIndex)
                  .classed('hover', isHoverOver);
            });
        }
    };

    // trigger calls from events too
    dispatch.on('elementMouseover.point', function(d) {
        if (interactive){
            chart._calls.highlightPoint(d.seriesIndex,d.pointIndex,true);
        }
    });

    dispatch.on('elementMouseout.point', function(d) {
        if (interactive){
            chart._calls.highlightPoint(d.seriesIndex,d.pointIndex,false);
        }
    });

    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        // width:   utils.getSet(width),

        width: {get: function(){return width;}, set: function(_){width=_;}},
        height: {get: function(){return height;}, set: function(_){height=_;}},
        xScale: {get: function(){return x;}, set: function(_){x=_;}},
        yScale: {get: function(){return y;}, set: function(_){y=_;}},
        pointScale: {get: function(){return z;}, set: function(_){z=_;}},
        xDomain: {
            get: function(){return xDomain;},
            set: function(_){xDomain=_;}
        },
        yDomain: {
            get: function(){return yDomain;},
            set: function(_){yDomain=_;}
        },
        pointDomain: {
            get: function(){return sizeDomain;},
            set: function(_){sizeDomain=_;}
        },
        xRange: {get: function(){return xRange;}, set: function(_){xRange=_;}},
        yRange: {get: function(){return yRange;}, set: function(_){yRange=_;}},
        pointRange: {
            get: function(){return sizeRange;},
            set: function(_){sizeRange=_;}
        },
        forceX: {get: function(){return forceX;}, set: function(_){forceX=_;}},
        forceY: {get: function(){return forceY;}, set: function(_){forceY=_;}},
        forcePoint: {
            get: function(){return forceSize;},
            set: function(_){forceSize=_;}
        },
        interactive: {
            get: function(){return interactive;},
            set: function(_){interactive=_;}
        },
        pointActive: {
            get: function(){return pointActive;},
            set: function(_){pointActive=_;}
        },
        padDataOuter:{
            get: function(){return padDataOuter;},
            set: function(_){padDataOuter=_;}
        },
        padData: {
            get: function(){return padData;},
            set: function(_){padData=_;}
        },
        clipEdge: {
            get: function(){return clipEdge;},
            set: function(_){clipEdge=_;}
        },
        clipVoronoi: {
            get: function(){return clipVoronoi;},
            set: function(_){clipVoronoi=_;}
        },
        clipRadius: {
            get: function(){return clipRadius;},
            set: function(_){clipRadius=_;}
        },
        showVoronoi: {
            get: function(){return showVoronoi;},
            set: function(_){showVoronoi=_;}
        },
        id: {get: function(){return id;}, set: function(_){id=_;}},


        // simple functor options
        x: {
            get: function(){return getX;},
            set: function(_){getX = d3.functor(_);}
        },
        y: {
            get: function(){return getY;},
            set: function(_){getY = d3.functor(_);}
        },
        pointSize: {
            get: function(){return getSize;},
            set: function(_){getSize = d3.functor(_);}
        },
        pointShape: {
            get: function(){return getShape;},
            set: function(_){getShape = d3.functor(_);}
        },

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = _.top    !== undefined ? _.top    : margin.top;
            margin.right  = _.right  !== undefined ? _.right  : margin.right;
            margin.bottom = _.bottom !== undefined ? _.bottom : margin.bottom;
            margin.left   = _.left   !== undefined ? _.left   : margin.left;
        }},
        duration: {
            get: function(){return duration;},
            set: function(_){
                duration = _;
                renderWatch.reset(duration);
            }
        },
        color: {
            get: function(){return color;},
            set: function(_){
                color = nv.utils.getColor(_);
            }
        },
        useVoronoi: {
            get: function(){return useVoronoi;},
            set: function(_){
                useVoronoi = _;
                if (useVoronoi === false) {
                    clipVoronoi = false;
                }
            }
        }
    });
    utils.initOptions(chart);
    return chart;
};

module.exports = {
    scatter: scatter
}

},{"../utils":20}],16:[function(require,module,exports){
"use strict";
var models = require("./scatter.js");
var d3 = window.d3;
var nv = window.nv;
var mytip = require("d3-tip")(d3);
var scatter_chart = function() {

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var scatter      = models.scatter();
    var xAxis        = nv.models.axis();
    var yAxis        = nv.models.axis();
    var legend       = nv.models.legend();
    var distX        = nv.models.distribution();
    var distY        = nv.models.distribution();
    var contentGenerator      = function(d){return d;};

    var margin       = {top: 30, right: 20, bottom: 50, left: 75};
    var width        = null;
    var height       = null;
    var container    = null;
    var color        = nv.utils.defaultColor();
    var x            = scatter.xScale();
    var y            = scatter.yScale();
    var showDistX    = false;
    var showDistY    = false;
    var showLegend   = true;
    var showXAxis    = true;
    var showYAxis    = true;
    var rightAlignYAxis = false;
    var state = nv.utils.state();
    var defaultState = null;
    var dispatch = d3.dispatch("stateChange", "changeState", "renderEnd");
    var noData       = null;
    var duration = 250;

    scatter.xScale(x).yScale(y);
    xAxis.orient("bottom").tickPadding(10);
    yAxis
        .orient((rightAlignYAxis) ? "right" : "left")
        .tickPadding(10)
    ;
    distX.axis("x");
    distY.axis("y");

    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var x0;
    var y0;
    var renderWatch = nv.utils.renderWatch(dispatch, duration);

    var stateGetter = function(data) {
        return function(){
            return {
                active: data.map(function(d) { return !d.disabled; })
            };
        };
    };

    var stateSetter = function(data) {
        return function(state) {
            if (state.active !== undefined)
                data.forEach(function(series,i) {
                    series.disabled = !state.active[i];
                });
        };
    };

    function chart(selection) {
        renderWatch.reset();
        renderWatch.models(scatter);
        if (showXAxis) renderWatch.models(xAxis);
        if (showYAxis) renderWatch.models(yAxis);
        if (showDistX) renderWatch.models(distX);
        if (showDistY) renderWatch.models(distY);

        selection.each(function(data) {
            var that = this;

            container = d3.select(this);
            nv.utils.initSVG(container);

            var availableWidth = nv.utils.availableWidth(width, container, margin),
                availableHeight = nv.utils.availableHeight(height, container, margin);

            chart.update = function() {
                if (duration === 0)
                    container.call(chart);
                else
                    container.transition().duration(duration).call(chart);
            };
            chart.container = this;

            state
                .setter(stateSetter(data), chart.update)
                .getter(stateGetter(data))
                .update();

            // DEPRECATED set state.disableddisabled
            state.disabled = data.map(function(d) { return !!d.disabled; });

            if (!defaultState) {
                var key;
                defaultState = {};
                for (key in state) {
                    if (state[key] instanceof Array)
                        defaultState[key] = state[key].slice(0);
                    else
                        defaultState[key] = state[key];
                }
            }

            // Display noData message if there"s nothing to show.
            if (!data || !data.length || !data.filter(function(d) { return d.values.length; }).length) {
                nv.utils.noData(chart, container);
                renderWatch.renderEnd("scatter immediate");
                return chart;
            } else {
                container.selectAll(".nv-noData").remove();
            }

            // Setup Scales
            x = scatter.xScale();
            y = scatter.yScale();

            // Setup containers and skeleton of chart
            var wrap = container.selectAll("g.nv-wrap.nv-scatterChart").data([data]);
            var wrapEnter = wrap.enter().append("g").attr("class", "nvd3 nv-wrap nv-scatterChart nv-chart-" + scatter.id());
            var gEnter = wrapEnter.append("g");
            var g = wrap.select("g");

            // background for pointer events
            gEnter.append("rect").attr("class", "nvd3 nv-background").style("pointer-events","none");

            gEnter.append("g").attr("class", "nv-x nv-axis");
            gEnter.append("g").attr("class", "nv-y nv-axis");
            gEnter.append("g").attr("class", "nv-scatterWrap");
            gEnter.append("g").attr("class", "nv-regressionLinesWrap");
            gEnter.append("g").attr("class", "nv-distWrap");
            gEnter.append("g").attr("class", "nv-legendWrap");

            if (rightAlignYAxis) {
                g.select(".nv-y.nv-axis")
                    .attr("transform", "translate(" + availableWidth + ",0)");
            }

            // Legend
            if (showLegend) {
                var legendWidth = availableWidth;
                legend.width(legendWidth);

                wrap.select(".nv-legendWrap")
                    .datum(data)
                    .call(legend);

                if ( margin.top != legend.height()) {
                    margin.top = legend.height();
                    availableHeight = nv.utils.availableHeight(height, container, margin);
                }

                wrap.select(".nv-legendWrap")
                    .attr("transform", "translate(0" + "," + (-margin.top) +")");
            }

            wrap.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Main Chart Component(s)
            scatter
                .width(availableWidth)
                .height(availableHeight)
                .color(data.map(function(d,i) {
                    d.color = d.color || color(d, i);
                    return d.color;
                }).filter(function(d,i) { return !data[i].disabled; }));

            wrap.select(".nv-scatterWrap")
                .datum(data.filter(function(d) { return !d.disabled; }))
                .call(scatter);


            // Setup Axes
            if (showXAxis) {
                xAxis
                    .scale(x)
                    ._ticks( nv.utils.calcTicksX(availableWidth/100, data) )
                    .tickSize( -availableHeight , 0);

                g.select(".nv-x.nv-axis")
                    .attr("transform", "translate(0," + y.range()[0] + ")")
                    .call(xAxis);
            }

            if (showYAxis) {
                yAxis
                    .scale(y)
                    ._ticks( nv.utils.calcTicksY(availableHeight/36, data) )
                    .tickSize( -availableWidth, 0);

                g.select(".nv-y.nv-axis")
                    .call(yAxis);
            }

            //============================================================
            // Event Handling/Dispatching (in chart"s scope)
            //------------------------------------------------------------

            legend.dispatch.on("stateChange", function(newState) {
                for (var key in newState)
                    state[key] = newState[key];
                dispatch.stateChange(state);
                chart.update();
            });

            // Update chart from a state object passed to event handler
            dispatch.on("changeState", function(e) {
                if (typeof e.disabled !== "undefined") {
                    data.forEach(function(series,i) {
                        series.disabled = e.disabled[i];
                    });
                    state.disabled = e.disabled;
                }
                chart.update();
            });

            var tip = mytip()
                .attr("class", "tip")
                .html(function(d) {
                    return contentGenerator(d);
                });

            var points = d3.select(this).selectAll("circle.nv-point");

            points.each(function(d) {
                d3.select(this).call(tip);
            });

            points
                .on("mouseenter", function(d, i){
                    tip.show(d, i);
                })
                .on("mouseleave", tip.hide);


            // store old scales for use in transitions on update
            x0 = x.copy();
            y0 = y.copy();

        });

        renderWatch.renderEnd("scatter with line immediate");
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    // expose chart"s sub-components
    chart.dispatch = dispatch;
    chart.scatter = scatter;
    chart.legend = legend;
    chart.xAxis = xAxis;
    chart.yAxis = yAxis;
    chart.distX = distX;
    chart.distY = distY;

    chart.options = nv.utils.optionsFunc.bind(chart);
    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        contentGenerator: {
            get: function(){return contentGenerator;},
            set: function(_){contentGenerator=_; }
        },
        width: {get: function(){return width;}, set: function(_){width=_;}},
        height:     {get: function(){return height;}, set: function(_){height=_;}},
        container:  {get: function(){return container;}, set: function(_){container=_;}},
        showDistX:  {get: function(){return showDistX;}, set: function(_){showDistX=_;}},
        showDistY:  {get: function(){return showDistY;}, set: function(_){showDistY=_;}},
        showLegend: {get: function(){return showLegend;}, set: function(_){showLegend=_;}},
        showXAxis:  {get: function(){return showXAxis;}, set: function(_){showXAxis=_;}},
        showYAxis:  {get: function(){return showYAxis;}, set: function(_){showYAxis=_;}},
        defaultState:     {get: function(){return defaultState;}, set: function(_){defaultState=_;}},
        noData:     {get: function(){return noData;}, set: function(_){noData=_;}},
        duration:   {get: function(){return duration;}, set: function(_){duration=_;}},

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = _.top    !== undefined ? _.top    : margin.top;
            margin.right  = _.right  !== undefined ? _.right  : margin.right;
            margin.bottom = _.bottom !== undefined ? _.bottom : margin.bottom;
            margin.left   = _.left   !== undefined ? _.left   : margin.left;
        }},
        rightAlignYAxis: {get: function(){return rightAlignYAxis;}, set: function(_){
            rightAlignYAxis = _;
            yAxis.orient( (_) ? "right" : "left");
        }},
        color: {get: function(){return color;}, set: function(_){
            color = nv.utils.getColor(_);
            legend.color(color);
            distX.color(color);
            distY.color(color);
        }}
    });

    nv.utils.inheritOptions(chart, scatter);
    nv.utils.initOptions(chart);
    return chart;
};


module.exports = {
    scatter_chart: scatter_chart
}

},{"./scatter.js":15,"d3-tip":27}],17:[function(require,module,exports){

var pretty_numbers = function(d){
    if(Math.abs(d)>1000000){return (d/1000000).toFixed(0) + "M";}
    else if(Math.abs(d)>1000){return (d/1000).toFixed(0) + "K";}
    else { return d; }
}
var pretty_times = function(d){
    return String(d).toHHMMSS();
}

var minimap_x = function(width, height){
    width = Math.min(width, height);
    return d3.scale.linear().domain([68,186]).range([
      .025*width, .973*width
    ]);
}

var minimap_y = function(width, height){
    height = Math.min(width, height);
    return d3.scale.linear().domain([68,186]).range([
        .94*height, 0.03*height,
        // .95*height, 0.03*height,
    ]);
}



module.exports = {
    pretty_numbers: pretty_numbers,
    pretty_times: pretty_times,
    minimap_x: minimap_x,
    minimap_y: minimap_y,
}

},{}],18:[function(require,module,exports){
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

},{}],19:[function(require,module,exports){
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

},{}],20:[function(require,module,exports){
'use strict';

var svg = require('./svg.js');
var axis_format = require('./axis_format.js');
var blanks = require('./blanks.js');
var reduce = require('./reduce.js');
var map = require('./map.js');
var parse_urls = require('./parse_urls.js');
var reshape = require('./reshape.js');
var filter = require('./filter.js');
var visuals = require('./visuals.js');

var getSet = function(value){
    var val = value;
    return {
        get: function(){
            return val;
        },
        set: function(_){
            val=_;
        }
    }
};

var getSetFunctor = function(value){
    var val = value;
    return {
        get: function(){
            return val;
        },
        set: function(_){
            val=d3.functor(_);

        }
    }
};

/*
Add a particular option from an options object onto chart
Options exposed on a chart are a getter/setter function that returns chart
on set to mimic typical d3 option chaining, e.g. svg.option1('a').option2('b');
option objects should be generated via Object.create() to provide
the option of manipulating data via get/set functions.
*/
var initOption = function(chart, name) {
    // if it's a call option, just call it directly, otherwise do get/set
    if (chart._calls && chart._calls[name]) {
        chart[name] = chart._calls[name];
    } else {
        chart[name] = function (_) {

            if (!arguments.length) return chart._options[name];
            chart._overrides[name] = true;
            chart._options[name] = _;
            return chart;
        };
        // calling the option as _option will ignore if set by option already
        // so nvd3 can set options internally but then stop if set manually
        chart['_' + name] = function(_) {
            if (!arguments.length) return chart._options[name];
            if (!chart._overrides[name]) {
                chart._options[name] = _;
            }
            return chart;
        }
    }
};


/*
Add all options in an options object to the chart
*/
var initOptions = function(chart) {
    chart._overrides = chart._overrides || {};
    var ops = Object.getOwnPropertyNames(chart._options || {});
    var calls = Object.getOwnPropertyNames(chart._calls || {});
    ops = ops.concat(calls);
    for (var i in ops) {
        initOption(chart, ops[i]);
    }
};

module.exports = {
    visuals: visuals,
    svg: svg,
    blanks: blanks,
    axis_format: axis_format,
    reduce: reduce,
    parse_urls: parse_urls,
    map: map,
    reshape: reshape,
    filter: filter,
    getSet: getSet,
    getSetFunctor: getSetFunctor,
    initOptions: initOptions,
}

},{"./axis_format.js":17,"./blanks.js":18,"./filter.js":19,"./map.js":21,"./parse_urls.js":22,"./reduce.js":23,"./reshape.js":24,"./svg.js":25,"./visuals.js":26}],21:[function(require,module,exports){
'use strict';

var count = function(){
    return function(msg, idx, ary){
      var prev_index = idx-1;
      if (prev_index >= 0 && prev_index < ary.length){
        var prev_value = ary[prev_index].sum;
        msg.sum = prev_value + 1;
      } else{
        msg.sum = 1;
      }
      return msg;
    };
};

var sum = function(){

    return function(msg, idx, ary){

      var prev_index = idx-1;

      var adder;
      if (msg.hasOwnProperty('value')){
        adder = msg.value;
      } else{
        adder = 1;
      }
      if (prev_index >= 0 && prev_index < ary.length){
        var prev_value = ary[prev_index].sum;
        msg.sum = prev_value + adder;
      } else{
        msg.sum = adder;
      }
      return msg;
    };
};

module.exports = {
    count: count,
    sum: sum,
};

},{}],22:[function(require,module,exports){
"use strict";


if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != "undefined" ? args[number] : match;
    });
  };
};

var version = 2;
var parse_url = "https://s3.amazonaws.com/datadrivendota/processed_replay_parse/";

// https://s3.amazonaws.com/datadrivendota/processed_replay_parse/2107579100_130_combatlog_item_buys_v1.json.gz
var url_for = function(shard, facet, logtype){
    return parse_url+"{0}_{1}_{2}_{3}_v{4}.json.gz".format(
        shard.match_id, shard.dataslice, logtype, facet, version
    );
};

module.exports = {
    url_for: url_for,
}

},{}],23:[function(require,module,exports){
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

},{}],24:[function(require,module,exports){
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

},{}],25:[function(require,module,exports){
function square_svg(destination, width, height){
  if (width === undefined){
    width = $(destination).width();
  }
  if (height === undefined){
    height = width;
  }
  return d3.select(destination)
    .append("svg")
    .attr("class", 'ddd-svg')
    .attr("width", width)
    .attr("height", width);
}

module.exports = {
  square_svg: square_svg,
}

},{}],26:[function(require,module,exports){
'use strict';

var $ = window.$;

var toggle_sides = function(){

  var idx = 0;
  var switching = function(){
    if(idx===0){
      $(' div.toggling g.nv-series-0, div.toggling g.nv-series-1, div.toggling g.nv-series-2, div.toggling g.nv-series-3, div.toggling g.nv-series-4').fadeIn();

      $(' div.toggling g.nv-series-5, div.toggling g.nv-series-6, div.toggling g.nv-series-7, div.toggling g.nv-series-8, div.toggling g.nv-series-9').fadeOut();

    }else if(idx==1){
      $(' div.toggling g.nv-series-0, div.toggling g.nv-series-1, div.toggling g.nv-series-2, div.toggling g.nv-series-3, div.toggling g.nv-series-4').fadeOut();

      $(' div.toggling g.nv-series-5, div.toggling g.nv-series-6, div.toggling g.nv-series-7, div.toggling g.nv-series-8, div.toggling g.nv-series-9').fadeIn();

    }else if(idx==2){
      $(' div.toggling g.nv-series-0, div.toggling g.nv-series-1, div.toggling g.nv-series-2, div.toggling g.nv-series-3, div.toggling g.nv-series-4').fadeIn();

      $(' div.toggling g.nv-series-5, div.toggling g.nv-series-6, div.toggling g.nv-series-7, div.toggling g.nv-series-8, div.toggling g.nv-series-9').fadeIn();
    }
    idx = (idx + 1)%3;
    recur = setTimeout(switching, 3000);
  };

  var recur;

  $('#start-fade').click(function(){
    $('#stop-fade, #start-fade').toggle();
    recur = setTimeout(switching, 3000);
  });
  $('#stop-fade').click(function(){
    $('#stop-fade, #start-fade').toggle();
    clearTimeout(recur);
  });

  $('#start-fade').click();
};

module.exports = {
    toggle_sides: toggle_sides
}

},{}],27:[function(require,module,exports){
// d3.tip
// Copyright (c) 2013 Justin Palmer
//
// Tooltips for d3.js SVG visualizations

(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    // AMD. Register as an anonymous module with d3 as a dependency.
    define(['d3'], factory)
  } else if (typeof module === 'object' && module.exports) {
    // CommonJS
    module.exports = function(d3) {
      d3.tip = factory(d3)
      return d3.tip
    }
  } else {
    // Browser global.
    root.d3.tip = factory(root.d3)
  }
}(this, function (d3) {

  // Public - contructs a new tooltip
  //
  // Returns a tip
  return function() {
    var direction = d3_tip_direction,
        offset    = d3_tip_offset,
        html      = d3_tip_html,
        node      = initNode(),
        svg       = null,
        point     = null,
        target    = null

    function tip(vis) {
      svg = getSVGNode(vis)
      point = svg.createSVGPoint()
      document.body.appendChild(node)
    }

    // Public - show the tooltip on the screen
    //
    // Returns a tip
    tip.show = function() {
      var args = Array.prototype.slice.call(arguments)
      if(args[args.length - 1] instanceof SVGElement) target = args.pop()

      var content = html.apply(this, args),
          poffset = offset.apply(this, args),
          dir     = direction.apply(this, args),
          nodel   = d3.select(node),
          i       = directions.length,
          coords,
          scrollTop  = document.documentElement.scrollTop || document.body.scrollTop,
          scrollLeft = document.documentElement.scrollLeft || document.body.scrollLeft

      nodel.html(content)
        .style({ opacity: 1, 'pointer-events': 'all' })

      while(i--) nodel.classed(directions[i], false)
      coords = direction_callbacks.get(dir).apply(this)
      nodel.classed(dir, true).style({
        top: (coords.top +  poffset[0]) + scrollTop + 'px',
        left: (coords.left + poffset[1]) + scrollLeft + 'px'
      })

      return tip
    }

    // Public - hide the tooltip
    //
    // Returns a tip
    tip.hide = function() {
      var nodel = d3.select(node)
      nodel.style({ opacity: 0, 'pointer-events': 'none' })
      return tip
    }

    // Public: Proxy attr calls to the d3 tip container.  Sets or gets attribute value.
    //
    // n - name of the attribute
    // v - value of the attribute
    //
    // Returns tip or attribute value
    tip.attr = function(n, v) {
      if (arguments.length < 2 && typeof n === 'string') {
        return d3.select(node).attr(n)
      } else {
        var args =  Array.prototype.slice.call(arguments)
        d3.selection.prototype.attr.apply(d3.select(node), args)
      }

      return tip
    }

    // Public: Proxy style calls to the d3 tip container.  Sets or gets a style value.
    //
    // n - name of the property
    // v - value of the property
    //
    // Returns tip or style property value
    tip.style = function(n, v) {
      if (arguments.length < 2 && typeof n === 'string') {
        return d3.select(node).style(n)
      } else {
        var args =  Array.prototype.slice.call(arguments)
        d3.selection.prototype.style.apply(d3.select(node), args)
      }

      return tip
    }

    // Public: Set or get the direction of the tooltip
    //
    // v - One of n(north), s(south), e(east), or w(west), nw(northwest),
    //     sw(southwest), ne(northeast) or se(southeast)
    //
    // Returns tip or direction
    tip.direction = function(v) {
      if (!arguments.length) return direction
      direction = v == null ? v : d3.functor(v)

      return tip
    }

    // Public: Sets or gets the offset of the tip
    //
    // v - Array of [x, y] offset
    //
    // Returns offset or
    tip.offset = function(v) {
      if (!arguments.length) return offset
      offset = v == null ? v : d3.functor(v)

      return tip
    }

    // Public: sets or gets the html value of the tooltip
    //
    // v - String value of the tip
    //
    // Returns html value or tip
    tip.html = function(v) {
      if (!arguments.length) return html
      html = v == null ? v : d3.functor(v)

      return tip
    }

    function d3_tip_direction() { return 'n' }
    function d3_tip_offset() { return [0, 0] }
    function d3_tip_html() { return ' ' }

    var direction_callbacks = d3.map({
      n:  direction_n,
      s:  direction_s,
      e:  direction_e,
      w:  direction_w,
      nw: direction_nw,
      ne: direction_ne,
      sw: direction_sw,
      se: direction_se
    }),

    directions = direction_callbacks.keys()

    function direction_n() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.n.y - node.offsetHeight,
        left: bbox.n.x - node.offsetWidth / 2
      }
    }

    function direction_s() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.s.y,
        left: bbox.s.x - node.offsetWidth / 2
      }
    }

    function direction_e() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.e.y - node.offsetHeight / 2,
        left: bbox.e.x
      }
    }

    function direction_w() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.w.y - node.offsetHeight / 2,
        left: bbox.w.x - node.offsetWidth
      }
    }

    function direction_nw() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.nw.y - node.offsetHeight,
        left: bbox.nw.x - node.offsetWidth
      }
    }

    function direction_ne() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.ne.y - node.offsetHeight,
        left: bbox.ne.x
      }
    }

    function direction_sw() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.sw.y,
        left: bbox.sw.x - node.offsetWidth
      }
    }

    function direction_se() {
      var bbox = getScreenBBox()
      return {
        top:  bbox.se.y,
        left: bbox.e.x
      }
    }

    function initNode() {
      var node = d3.select(document.createElement('div'))
      node.style({
        position: 'absolute',
        top: 0,
        opacity: 0,
        'pointer-events': 'none',
        'box-sizing': 'border-box'
      })

      return node.node()
    }

    function getSVGNode(el) {
      el = el.node()
      if(el.tagName.toLowerCase() === 'svg')
        return el

      return el.ownerSVGElement
    }

    // Private - gets the screen coordinates of a shape
    //
    // Given a shape on the screen, will return an SVGPoint for the directions
    // n(north), s(south), e(east), w(west), ne(northeast), se(southeast), nw(northwest),
    // sw(southwest).
    //
    //    +-+-+
    //    |   |
    //    +   +
    //    |   |
    //    +-+-+
    //
    // Returns an Object {n, s, e, w, nw, sw, ne, se}
    function getScreenBBox() {
      var targetel   = target || d3.event.target;

      while ('undefined' === typeof targetel.getScreenCTM && 'undefined' === targetel.parentNode) {
          targetel = targetel.parentNode;
      }

      var bbox       = {},
          matrix     = targetel.getScreenCTM(),
          tbbox      = targetel.getBBox(),
          width      = tbbox.width,
          height     = tbbox.height,
          x          = tbbox.x,
          y          = tbbox.y

      point.x = x
      point.y = y
      bbox.nw = point.matrixTransform(matrix)
      point.x += width
      bbox.ne = point.matrixTransform(matrix)
      point.y += height
      bbox.se = point.matrixTransform(matrix)
      point.x -= width
      bbox.sw = point.matrixTransform(matrix)
      point.y -= height / 2
      bbox.w  = point.matrixTransform(matrix)
      point.x += width
      bbox.e = point.matrixTransform(matrix)
      point.x -= width / 2
      point.y -= height / 2
      bbox.n = point.matrixTransform(matrix)
      point.y += height
      bbox.s = point.matrixTransform(matrix)

      return bbox
    }

    return tip
  };

}));

},{}]},{},[11])(11)
});