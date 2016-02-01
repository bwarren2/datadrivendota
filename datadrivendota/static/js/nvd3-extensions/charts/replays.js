"use strict";
var utils = require("../utils");
var tooltips = require("./tooltips");
var Promise = require("bluebird");
var $ = window.$;
var nv = window.nv;
var _ = window._;


var timeToSecs = function(time){
    return parseInt(time.split(":")[0])*60+parseInt(time.split(":")[1]);
};

// Things uses in the pmses:
// d.hero.name (for labeling)
// d.lookup_pair (for hitting s3)
// Using radiant or dire numbers should fake those members.
var state_lineup = function(pmses, facet, destination, params){

  // Get the replay parse info
  Promise.all(
    pmses.map(function(pms){
      var location = utils.parse_urls.url_for(pms, facet, 'statelog');
      return $.getJSON(location);
    })
  ).then(function(facets){

    // Structure the fancy filtering we are about to do.
    var width;
    var height;
    var start;
    var stop;
    var interpolation;
    var stride;
    var chart_destination = destination+" .chart";
    var label_destination = destination+" label";
    var x_label = toTitleCase("offset time");
    var y_label = toTitleCase(facet);

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
        return x.offset_time <= stop && x.offset_time >= start && x.offset_time.mod(stride) === 0
      });
      return {
        key: "{0}, M#{1}".format(pmses[i].hero.name, pmses[i].match.steam_id),
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
            left: 50,
            bottom: 50,
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


/**
 * Merges two data series that have the same periodicity but uneven starts.
 * @param {array} data - The array of unevenly spaced series.
 * @param {string} attr - The named attribute of the data samples to use.
 * @param {integer} stride - The spacing of the series (ex -10, 0, 10...) = 10.
 */
var scatterline_merge = function(data, attr, stride){

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
      x_val = x0[attr];
    }
    else if(i > x0.offset_time && i < x1.offset_time){
      // Ex 5, 10, 15, 20.  idx for 20 = (20-5)/5 = 3
      var series_idx = (i-x0.offset_time)/stride
      x_val = x[series_idx][attr];
    } else {
      x_val = x1[attr];
    }

    var y_val;
    if (i <= y0.offset_time) {
      y_val = y0[attr];
    }
    else if(i > y0.offset_time && i <= y1.offset_time){
      var series_idx = (i-y0.offset_time)/stride
      y_val = y[series_idx][attr];
    } else {
      y_val = y1[attr];
    }

    return_lst.push({
      offset_time: i,
      x: x_val,
      y: y_val,
    })
  };

  return return_lst;
}

var scatterline = function(pmses, destination, params, attr, logtype){

  // Get the replay parse info
  Promise.all(
    pmses.map(function(pms){
      var location = utils.parse_urls.url_for(pms, attr, logtype);
      return $.getJSON(location);
    })
  ).then(function(data){
    // Structure the fancy filtering we are about to do.

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

    var values = scatterline_merge(trimmed_data, attr, stride)

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
      key: toTitleCase(attr),
      values: values
    }];

    $(chart_destination).empty();
    $(label_destination).html(toTitleCase(attr));

    var true_min = d3.min(trimmed_data, function(series){
      return d3.min(series, function(nested){
        return nested[attr];
      })
    });

    var true_max = d3.max(trimmed_data, function(series){
      return d3.max(series, function(nested){
        return nested[attr];
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
          // .useVoronoi(false)

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
      var y_index = y_data.findIndex(function(y_item){
        var this_hash = hasher(y_item);
        return this_hash===hash;
      });

      if(y_index===undefined) console.log('Freak');

      y_data = winnow(y_data, y_index);
      return_obj['y'] = y_data[y_index].offset_time;

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

var item_scatter = function(pmses, destination, params){

  // Get the replay parse info
  Promise.all(
    pmses.map(function(pms){
      var location = utils.parse_urls.url_for(pms, 'item_buys', 'combatlog');
      return $.getJSON(location);
    })
  ).then(function(data){
    // Structure the fancy filtering we are about to do.
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
        return x.offset_time <= stop && x.offset_time >= start
      });
      return filtered_dataset;
    });

    console.log(trimmed_data);
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
      });
  });
};


module.exports = {
  state_lineup: state_lineup,
  scatterline: scatterline,
  item_scatter: item_scatter,
};
