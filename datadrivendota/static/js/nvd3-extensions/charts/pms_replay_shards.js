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
