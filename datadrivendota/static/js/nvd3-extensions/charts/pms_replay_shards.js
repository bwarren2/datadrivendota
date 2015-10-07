"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var tooltips = require("./tooltips.js");

var shard_lineup = function(destination, params){
  Promise.join(
    $.ajax({
        url: "https://s3.amazonaws.com/datadrivendota/media/playermatchsummaries/replays/1837060998_1_parse_shard.json.gz",
        dataType: "json",
    }),
    $.ajax({
        url: "https://s3.amazonaws.com/datadrivendota/media/playermatchsummaries/replays/1837060998_130_parse_shard.json.gz",
        dataType: "json",
    })

  ).then(function(data){
    console.log(data);
    $(destination).empty();
    var plot_data = data.map(function(d){
      var cumsum = 0;
      return {
        "key": toTitleCase(d[0].unit),
        "values": d.filter(function(m){
          return m.type == "gold_reasons";
        }).map(function(m){
          m.cumsum = cumsum + m.value;
          cumsum += m.value;
          return m;
        })
      };
    });
    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);

    var xlab = "Time";
    var ylab = "Gold";

    nv.addGraph(

      function(){
        chart = nv.models.lineChart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .x(function(d){return d.offset_time;})
          .y(function(d){return d.cumsum;})
          .showLegend(false)
          .interpolate('step-after');

        chart.xAxis.axisLabel(xlab);
        chart.yAxis.axisLabel(ylab).axisLabelDistance(-20);

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      }
    );

  }).catch(function(e){
    console.log(e);
  });
};
module.exports = {
  shard_lineup: shard_lineup
};
