"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
var $ = window.$;
var nv = window.nv;
var _ = window._;


// Things uses in the pmses:
// d.hero.name (for labeling)
// d.lookup_pair (for hitting s3)
// Using radiant or dire numbers should fake those members.

var state_lineup = function(pmses, facet, destination, params){

  // Get the replay parse info
  Promise.all(
    pmses.map(function(pms){
      var location = utils.parse_urls.url_for(pms, facet);
      return $.getJSON(location);
    })
  ).then(function(facets){

    // Structure the fancy filtering we are about to do.

    var timeToSecs = function(time){
        return parseInt(time.split(":")[0])*60+parseInt(time.split(":")[1]);
    };

    var width;
    var height;
    var start;
    var stop;
    var interpolation;
    var stride;
    var chart_destination = destination+" .chart";
    var label_destination = destination+" label";
    var x_label = toTitleCase("offset time".replace(/\_/g, " "));
    var y_label = toTitleCase(facet.replace(/\_/g, " "));

    if(params!==undefined){

      if(params.start_time!==undefined&params.start_time!==""){
        start = timeToSecs(params.start_time);
      } else {
        start = -10000;
      }

      if(params.end_time!==undefined&params.end_time!==""){
        stop = timeToSecs(params.end_time);
      } else {
        stop = 10000;
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

    var plot_data = facets.map(function(d, i){
      var filtered_dataset = d.filter(function(x){
        return x.offset_time <= stop & x.offset_time >= start;
      }).filter(function(x){
        return x.offset_time.mod(stride) === 0;
      });
      return {
        key: pmses[i].hero.name,
        values: filtered_dataset,
      };
    });

    $(chart_destination).empty();
    $(label_destination).html(y_label);

    var svg = utils.svg.square_svg(chart_destination, width, height);
    nv.addGraph(

      function(){
        var chart = nv.models.lineChart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .x(function(d){
            return d.offset_time;
          })
          .y(function(d){
            return d[facet];
          })
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


        chart.xAxis.axisLabel(x_label).tickFormat(
          function(d){
            return String(d).toHHMMSS();
          }
        );

        chart.yAxis.axisLabel(y_label).axisLabelDistance(-18)
          .tickFormat(
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
};

module.exports = {
  state_lineup: state_lineup,
};
