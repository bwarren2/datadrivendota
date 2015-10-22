"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
var AjaxCache = require("../ajax_cache");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var tooltips = require("./tooltips.js");

var shard_lineup = function(
  pms_ids,
  msg_filter,
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
    )
  }).then(function(data){

    // Clear the div
    $(destination).empty();

    data = utils.reshape.pms_merge(data, pmses);

    data = data.map(function(d){
      return {
        icon: d.icon,
        values: d.values.filter(msg_filter(d.icon))
      };
    });

    // Reshape into something else if needed.
    data = msg_reshape(data);


    var key_fn = function(d){
      return d.hero.name;
    };
    // Filter, map, cast data into plotting format
    var plot_data = data.map(function(d){
      return {
        "key": key_fn(d.icon),
        "values": d.values.map(msg_map(d.icon))
      };
    });

    var svg = utils.svg.square_svg(destination);
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
          .forceY(0)
          .forceX(0);

        chart.xAxis.axisLabel(x_data.label).tickFormat(
          function(d){
            return moment.duration(d*1000).asMinutes().toFixed(2)
          }
        );
        chart.yAxis.axisLabel(y_data.label).axisLabelDistance(-20).tickFormat(
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

  }).catch(function(e){
    console.log(e);
  });
};

module.exports = {
  shard_lineup: shard_lineup,
};
