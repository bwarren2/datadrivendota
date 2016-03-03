"use strict";

var utils = require("../utils");
var Promise = require("bluebird");
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
          return {
            y: d[y_var],
            x: d.hero.name,
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
            bottom: 105,
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
          .attr("transform", function(d, i, j) {
            return "translate (-7, 65) rotate(-90 0,0)"
          }) ;
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
