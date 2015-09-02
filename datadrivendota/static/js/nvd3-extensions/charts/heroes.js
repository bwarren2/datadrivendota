"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
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
  );
}

var classify_bars = function(destination){

  var place = destination + " rect.discreteBar";
  d3.selectAll(place).attr(
    "class",
    function(d){
        var hero = d.hero;
        return d3.select(this).attr("class")+ " hero-datum "+hero.css_classes;
    }
  );
}


var pickban_scatter = function(destination, params){

  var winrate_data;
  var dossiers;
  var blanks;

  Promise.join(
    $.ajax(
      "/rest-api/match-pickban/?" + $.param(params)
    ),
    $.ajax(
      "/rest-api/hero-dossiers/"
    )
  ).then(function(data){
    winrate_data = data[0];
    dossiers = data[1];
    blanks = utils.blanks.blank_hero_pickbans(dossiers);
    $(destination).empty();
    return winrate_data.slice(0, 1);
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


var winrate_scatter = function(destination, params){

  var winrate_data;
  var dossiers;
  var blanks;

  Promise.join(
    $.ajax(
      "/rest-api/match-pickban/?" + $.param(params)
    ),
    $.ajax(
      "/rest-api/hero-dossiers/"
    )
  ).then(function(data){
    winrate_data = data[0];
    dossiers = data[1];
    blanks = utils.blanks.blank_hero_pickbans(dossiers);
    $(destination).empty();
    return winrate_data.slice(0, 1);

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

var quality_barchart = function(destination, params){

  var winrate_data;
  var dossiers;
  var blanks;

  Promise.join(
    $.ajax(
      "/rest-api/match-pickban/?" + $.param(params)
    ),
    $.ajax(
      "/rest-api/hero-dossiers/"
    )
  ).then(function(data){
    winrate_data = data[0];
    dossiers = data[1];
    blanks = utils.blanks.blank_hero_pickbans(dossiers);
    $(destination).empty();
    return winrate_data.slice(0, 1);
  })
  .then(function(working_set){
    var plot_data = d7.extensions.utils.reduce.extract_pickbans(
      blanks, working_set
    );
    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);
    var xlab = "Hero";
    var ylab = "relative Strength";

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
