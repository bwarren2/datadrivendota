"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var tooltips = require("./tooltips.js");



var pms_scatter = function(destination, params, x_var, y_var, x_lab, y_lab){

  Promise.resolve(
    $.ajax(
      "/rest-api/player-match-summary/?" + $.param(params)
    )
  ).then(function(pmses){
    $(destination).empty();
    var plot_data = [
        {
            "key": x_lab + " vs " + y_lab,
            "values": pmses.map(
            function(d){
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
            left: 45,
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
        chart.yAxis.axisLabel(y_lab).axisLabelDistance(-20);

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
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
    $.ajax(
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

        chart = nv.models.lineChart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .showLegend(true);

        chart.xAxis.axisLabel("Level");
        chart.yAxis.axisLabel("Time");

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
    $.ajax(
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
    console.log(plot_data);

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
        chart.yAxis.axisLabel(y_lab);

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
};