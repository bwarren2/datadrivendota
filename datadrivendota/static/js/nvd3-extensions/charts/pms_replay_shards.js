"use strict";
var utils = require("../utils");
var components = require("../components");
var Promise = require("bluebird");
var AjaxCache = require("../ajax_cache");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
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
    pmses
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
    };

    return {
      icon: d.icon,
      values: data_values
    };
  });

  // Reshape into something else if needed.
  data = msg_reshape(data);


  // Filter, map, cast data into plotting format
  var plot_data = data.map(function(d){
    return {
      "key": d.icon.key_name,
      "values": d.values.map(msg_map(d.icon))
    };
  });
  plot_data = endcap(plot_data);

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
var special_shard_lineup = function(destination){

  var url ="/rest-api/player-match-summary/?match_id=1843672837";
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

    $("button#draw").on("click", function(){

        var rollup_map = {
            players: utils.reshape.noop,
            sides: utils.reshape.sides,
            match: utils.reshape.matches,
        };
        var rollup_fn = rollup_map[$("select#rollup ").val()];

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
            selected_data.push(data[parseInt(id)])
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
          destination,
          pmses
        );

    });


  }).catch(function(e){
    console.log(e);
  });
};


module.exports = {
  shard_lineup: shard_lineup,
  special_shard_lineup: special_shard_lineup,
};
