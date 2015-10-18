"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
var AjaxCache = require("../ajax_cache");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var tooltips = require("./tooltips.js");

var shard_lineup = function(destination, params){
  Promise.join(
    AjaxCache.get({
        url: "https://s3.amazonaws.com/datadrivendota/media/playermatchsummaries/replays/1837060998_1_parse_shard.json.gz",
        dataType: "json",
    }),
    AjaxCache.get({
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

var hack = function(destination, params){
    Promise.resolve(
        AjaxCache.get({
            url: 'https://s3.amazonaws.com/datadrivendota/raw_replay_parse/1843672837_raw_parse.json',
            dataType: 'json'
        })
    ).then(function(data){
        console.log(data)
    }).catch(function(jqXhr, err, errStr){
        // console.log('Error :(');
        // console.log(jqXhr);
        // console.log(jqXhr.responseText);
        // console.log(jqXhr.status);
        // console.log(jqXhr.statusText);
        // console.log(jqXhr.statusCode());
    })
};

module.exports = {
  shard_lineup: shard_lineup,
  hack: hack,
};
