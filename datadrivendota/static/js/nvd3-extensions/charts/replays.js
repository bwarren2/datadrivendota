"use strict";
var utils = require("../utils");
var tooltips = require("./tooltips");
var Promise = require("bluebird");
var Handlebars = window.Handlebars;
var $ = window.$;
var nv = window.nv;
var _ = window._;


var timeToSecs = function(time){
    return parseInt(time.split(":")[0])*60+parseInt(time.split(":")[1]);
};

var replay_lines = function(dataset, facet, destination, params){

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
    var show_legend = false;

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

      if(params.y_label!==undefined){
        y_label = params.y_label;
      }
      if(params.show_legend!==undefined){
        show_legend = params.show_legend;
      }
    }

    var plot_data = dataset.map(function(d, i){
      d.values = d.values.filter(function(x){
        return x.offset_time <= stop && x.offset_time >= start && x.offset_time.mod(stride) === 0;
      });
      return d;
    });

    $(chart_destination).empty();
    $(label_destination).html(y_label);

    var svg = utils.svg.square_svg(chart_destination, width, height);
    nv.addGraph(

      function(){
        var chart = nv.models.lineWithFocusChart()
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
          .showLegend(show_legend)
          .interpolate(interpolation)
          .forceY(0);

        chart.tooltip.contentGenerator(
          tooltips.noformat_tooltip('offset_time', facet)
        );

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

        chart.x2Axis.tickFormat(
          utils.axis_format.pretty_times
        );

        chart.xAxis.axisLabel(x_label).tickFormat(
          utils.axis_format.pretty_times
        );

        chart.yAxis.axisLabel(y_label).axisLabelDistance(-18).tickFormat(
          utils.axis_format.pretty_numbers
        );

        var chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      }
    );
}

var stat_lineup = function(shards, facet, destination, params, log){

  if (log===undefined){log = 'statelog';}

  if (log==='statelog'){facet='allstate';}

  // Get the replay parse info
  Promise.all(
    shards.map(function(shard){
      var location = utils.parse_urls.url_for(shard, facet, log);
      return $.getJSON(location);
    })
  ).then(function(facets){
    var dataset = facets.map(function(dataseries, i){
      var myobj =  {
        'key': shards[i].name,
        'css_classes': shards[i].css_classes,
        'values': dataseries
      };
      return myobj;
    });
    replay_lines(dataset, facet, destination, params);
  });
};


/**
 * Merges two data series that have the same periodicity but uneven starts.
 * @param {array} shardfacets - An array of 3-tuples: shard, facet, logtype.
 * @param {string} destination - Where to draw.
 * @param {integer} params - Adjustable stuffs.
 */
var multifacet_lineup = function(shardfacets, destination, params, label){

  // Get the replay parse info
  Promise.all(
    shardfacets.map(function(lst){
      var location = utils.parse_urls.url_for(lst[0], lst[1], lst[2]);
      return $.getJSON(location);
    })
  ).then(function(facets){

    var dataset = facets.map(function(dataseries, i){

      var values = dataseries.map(function(d){
          d.value = d[shardfacets[i][1]]
          return d;
        });
      var myobj =  {
        'key': shardfacets[i][0].name + ' ' + shardfacets[i][1],
        'css_classes': shardfacets[i][0].css_classes,
        'values': values
      };
      return myobj;
    });
    if (typeof label != 'undefined') {
      params.y_label = label;
    }
    replay_lines(dataset, 'value', destination, params);
  });
};


/**
 * Merges two data series that have the same periodicity but uneven starts.
 * @param {array} data - The array of unevenly spaced series.
 * @param {string} facet - The named stat of the data samples to use.
 * @param {integer} stride - The spacing of the series (ex -10, 0, 10...) = 10.
 */
var scatterline_merge = function(data, facet, stride){

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
      x_val = x0[facet];
    }
    else if(i > x0.offset_time && i < x1.offset_time){
      // Ex 5, 10, 15, 20.  idx for 20 = (20-5)/5 = 3
      var series_idx = (i-x0.offset_time)/stride
      x_val = x[series_idx][facet];
    } else {
      x_val = x1[facet];
    }

    var y_val;
    if (i <= y0.offset_time) {
      y_val = y0[facet];
    }
    else if(i > y0.offset_time && i <= y1.offset_time){
      var series_idx = (i-y0.offset_time)/stride
      y_val = y[series_idx][facet];
    } else {
      y_val = y1[facet];
    }

    return_lst.push({
      offset_time: i,
      x: x_val,
      y: y_val,
    })
  };

  return return_lst;
}

var scatterline = function(shards, facet, destination, params, logtype){

  // Get the replay parse info
  Promise.all(
    shards.map(function(shard){
      var location = utils.parse_urls.url_for(shard, facet, logtype);
      return $.getJSON(location);
    })
  ).then(function(data){

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

    var values = scatterline_merge(trimmed_data, facet, stride)

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
      key: toTitleCase(facet),
      values: values
    }];

    $(chart_destination).empty();
    $(label_destination).html(toTitleCase(facet));

    var true_min = d3.min(trimmed_data, function(series){
      return d3.min(series, function(nested){
        return nested[facet];
      })
    });

    var true_max = d3.max(trimmed_data, function(series){
      return d3.max(series, function(nested){
        return nested[facet];
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

function findById(source, target_hash, hasher) {
  for (var i = 0; i < source.length; i++) {
    if (hasher(source[i]) === target_hash) {
      return i;
    }
  }
  throw "Couldn't find object with id: " + id;
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

      var y_index = findById(y_data, hash, hasher);

      if(y_index===undefined) console.log('Freak');

      return_obj['y'] = y_data[y_index].offset_time;
      y_data.splice(y_index, 1);
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

var item_scatter = function(shards, destination, params){

  var urls = shards.map(function(shard){
      var location = utils.parse_urls.url_for(shard, 'item_buys', 'combatlog');
      return $.getJSON(location);
    })
    urls.push($.getJSON('/rest-api/items/'))

  // Get the replay parse info
  Promise.all(
    urls
  ).then(function(data){

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

    var cost_data = data.pop();
    var costs = cost_data.reduce(function(accu, item){
      accu[item.internal_name] = item.cost; return accu;
    }, {});
    // Trim down our data sets.
    var trimmed_data = data.map(function(d, i){
      var filtered_dataset = d.filter(function(x){
        return x.offset_time <= stop && x.offset_time >= start
      });
      return filtered_dataset;
    });

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


    var cost_radius = d3.scale.linear()
        .domain([
          0,
          500,
          1000,
          2000,
          3500,
          5000,
          6000,
          6999,
        ])
        .range([
          1,
          1.25,
          1.75,
          2,
          2.5,
          3,
          3.5,
          4,
        ]);


    values.map(function(d){
      var match = costs[d.item.substring(5)]
      if(match){
        d.cost = match;
      } else{
        d.cost = 0;
      }
      d.size = cost_radius(d.cost);
      return d
    })

    var cost_extent = d3.extent(plot_data[0].values, function(d){
      return d.cost;
    })

    var cost_color = d3.scale.linear()
        .domain([
          0, 499,
          500, 999,
          1000, 1999,
          2000, 3499,
          3500, 4999,
          5000, 5999,
          6000, 6999,
        ])
        .range([
          d3.rgb("black").brighter(.2), d3.rgb("black").darker(1.3),
          d3.rgb("red").brighter(.2), d3.rgb("red").darker(1.3),
          d3.rgb("orange").brighter(.2), d3.rgb("orange").darker(1.3),
          d3.rgb("yellow").brighter(.2), d3.rgb("yellow").darker(1.3),
          d3.rgb("green").brighter(.2), d3.rgb("green").darker(1.3),
          d3.rgb("blue").brighter(.2), d3.rgb("blue").darker(1.3),
          d3.rgb("violet").brighter(.2), d3.rgb("violet").darker(1.3),
        ]);

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
      },
      function(){
          d3.selectAll(destination+' .nv-point')
            .style("fill", function(d){return cost_color(d[0].cost)})
            .style('stroke', function(d){return cost_color(d[0].cost)})
            .style('stroke', function(d){return cost_color(d[0].cost)})
            .attr('r', function(d){return cost_radius(d[0].cost)})

      });
  });
};


var item_inventory = function(shards, destination, labels){

  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  })
  urls.push($.getJSON('/rest-api/items/'))
  // Get the replay parse info
  Promise.all(
    urls
  ).then(function(data){


    var cost_data = data.pop();
    var costs = cost_data.reduce(function(accu, item){
      accu[item.internal_name] = item.cost; return accu;
    }, {});
    // Trim down our data sets.

    var trimmed_data = data.map(function(series, i){
      var max = d3.max(series, function(d){return d.offset_time})
      var filtered_dataset = series.filter(function(x){
        return x.offset_time.mod(600) === 0 || x.offset_time == max;
      });
      return filtered_dataset;
    });

    var max_length = d3.max(trimmed_data, function(series){
      return series.length;
    });


    var prev_pms_time = -600;
    var table = '<table class="table  table-hover">';

    for (var time_idx=0; time_idx<max_length; time_idx++) {
      for(var series_idx = 0; series_idx<trimmed_data.length; series_idx++){


        var pms_label = labels[series_idx];
        var shard_id = shards[series_idx].id;
        var pms_time = trimmed_data[series_idx][time_idx].offset_time;

        table += '<tr class="inforow" data-shard-id="'+shard_id+'" data-min-time="'+prev_pms_time+'" data-max-time="'+pms_time+'">';

        table += '<td>'+pms_label+'</td>';

        if (trimmed_data[series_idx][time_idx]) {

          table += '<td>'+String(trimmed_data[series_idx][time_idx].offset_time).toHHMMSS()+'</td>';
        }else{

          table += '<td></td>';
        }
        var item_str = "";

        [
          'item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5'
        ].map(function(slot){
          var item;

          if (trimmed_data[series_idx][time_idx]) {
            item = trimmed_data[series_idx][time_idx][slot];
          }else{
            item = undefined;
          }

          if (item) {
            item_str+="<span><i class='d2items "+item.substring(5)+"'></i></span>"
          }else{
            item_str+="";
          }
        });

        table += '<td>'+item_str+'</td>';


        table += '</tr>';
      }
      table += '<tr class="spacer"><td></td><td></td><td></td></tr>';

      prev_pms_time = pms_time;

    }
    table += '</table>';
    $(destination+' #target').empty();
    $(destination+' #target').append(table);
    $(destination+' label').html('Inventory timings');
    $('.inforow').on('mouseover', function(){

      $(window).trigger('shardfilter', [
        $(this).data('shard-id'),
        $(this).data('min-time'),
        $(this).data('max-time'),
      ])
    });

  });
};

var minimap = function(shards, destination, params){

  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  })
  // Get the replay parse info
  Promise.all(urls).then(function(data){

    var css_class_swap = function(side){
      if (side === 'radiant') {
        return 'radiant-face-glow';
      }
      else if (side === 'dire') {
        return 'dire-face-glow';
      }
    }

    var position_data =  data.map(function(series, series_idx){
      return series.reduce(function(prev, d){
        prev[String(d.offset_time)] = {
          x: d.x,
          y: d.y,
          hero_name: shards[series_idx].hero_name,
          css_classes: css_class_swap(shards[series_idx].css_classes)
        }
        return prev;
      }, {})
    })

    var svg = make_map_background(destination)
    var width = svg.attr('width');
    var height = svg.attr('height');

    var fetch_data = position_data.map(function(d){
      return d[0]
    });

    var xscale = utils.axis_format.minimap_x(width, height);
    var yscale = utils.axis_format.minimap_y(width, height);

    var faces = d3.select(destination).selectAll('i').data(fetch_data)
      .enter()
      .append('i')
      .attr('class', function(d){
        return 'd2mh ' + d.hero_name + ' ' +d.css_classes;
      })
      .style('left', function(d){return xscale(d.x)+'px'})
      .style('bottom', function(d){return yscale(d.y)+'px'})
      .style('position', 'absolute')

    $(window).on('update', function(evt, arg){
      var fetch_data = position_data.map(function(d){
        return d[arg]
      });

      var faces = d3.select(destination).selectAll('i').data(fetch_data)
        .transition()
        .duration(1000)
        .style('left', function(d){
          if (d===undefined) {
            return xscale(0)+'px'
          }
          else{
            return xscale(d.x)+'px'
          }
        })
        .style('bottom', function(d){
          if (d===undefined) {
            return yscale(0)+'px'
          }else{
            return yscale(d.y)+'px'
          }
        }).ease("linear")

    })

  }).catch(function(e){
    console.log(e);
  })
};


var position_heatmap = function(shards, destination, params){
  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  })
  // Get the replay parse info
  Promise.all(urls).then(function(raw_data){

    $(destination+' .chart').empty();
    $(destination+' label').empty();
    $(destination+' .legend').empty();
    var svg = make_map_background(destination)
    var width = svg.attr('width');
    var height = svg.attr('height');

    var xscale = utils.axis_format.minimap_x(width, height);
    var yscale = utils.axis_format.minimap_y(width, height);

    var data = crosscount(raw_data[0]);

    var x_data = [1,5,10,30,60,120];
    var colors = d3.scale.linear()
    .domain(x_data)
    .range([
      d3.rgb("green"),
      d3.rgb("green").brighter(1),
      d3.rgb("orange"),
      d3.rgb("orange").brighter(1),
      d3.rgb("red"),
      d3.rgb("red").brighter(1),
    ]);

    var update_heat = function(data, label){
      var cards = svg.selectAll('.cell')
        .data(data,
          function(d) {return d.x+':'+d.y;}
        );

      cards.append("title");
      cards.select("title").text(function(d) { return d.ct; });

      var size = xscale(10)-xscale(9);

      cards.enter().append("rect")
          .attr("x", function(d) { return xscale(d.x)})
          .attr("y", function(d) { return height-yscale(d.y) })
          .attr("class", "cell")
          .attr("ddd-ct", function(d) { return d.ct })
          .attr("width", size+2)
          .attr("height", size+2)
          .style("fill", function(d){return colors(d.ct)})
          .style("stroke", function(d){return 'black'})
          .style("stroke-width", '1px')

      cards.transition().duration(1000)
          .style("fill", function(d) { return colors(d.ct); });


      cards.exit()
        .transition()
        .duration(1000)
        .style("opacity", 0)
        .remove();

      d3.select(destination+' label').html(label);
    }
    var get_label = function(shard, min_time, max_time){
      if (shard.label) {
        var prefix = shard.label;
      } else{
        var prefix = shard.name;
      }
      if(min_time!==undefined){
        return prefix+', '+String(min_time).toHHMMSS()+'-'+String(max_time).toHHMMSS()
      }else{
        return prefix+', all game'
      }
    }
    update_heat(data, get_label(shards[0]));




    var legend_data = x_data;
    var legend_width = $(destination).width();
    var legendElementWidth = legend_width/legend_data.length;
    var legend_height = legendElementWidth;

    var legend = d3.select(destination+' .legend')
      .append("svg")
      .attr("width", legend_width)
      .attr("height", legend_height);

    var selection = legend.selectAll('rect').data(legend_data).enter();

    selection.append("rect")
      .attr("x", function(d, i) { return legendElementWidth * i; })
      .attr("y", 0)
      .attr("width", legendElementWidth)
      .attr("height", legendElementWidth)
      .style("fill", function(d, i) {return colors(d); });


    selection.append("text")
      .attr("class", "legendtext")
      .text(function(d) {return "≥ " + Math.round(d)+'s'; })
      .attr("x", function(d, i) { return legendElementWidth * i+legendElementWidth/4; })
      .attr("y", legendElementWidth/2)
      .attr("fill", 'black');

    $(window).on('shardfilter', function(evt, id, min_time, max_time){
      var shard;
      var test = raw_data.filter(function(d, i){
        if (shards[i].id == id){
          shard = shards[i];
        }
        return shards[i].id == id;
      })[0].filter(function(d){
        return d.offset_time > min_time && d.offset_time <= max_time;
      });
      var updata = crosscount(test);
      update_heat(updata, get_label(shard, min_time, max_time));
    })


  })

}

var make_map_background = function(destination){
    var svg = utils.svg.square_svg(destination+' .chart');
    var width = svg.attr('width');
    var height = svg.attr('height');

    var defs = svg.append('svg:defs');

    defs.append("svg:pattern")
        .attr("id", "minimap_img")
        .attr("width", width)
        .attr("height", height)
        .attr("patternUnits", "userSpaceOnUse")
        .append("svg:image")
        .attr("xlink:href", 'https://s3.amazonaws.com/datadrivendota/images/minimap.png')
        .attr("width", width)
        .attr("height", height)
        .attr("x", 0)
        .attr("y", 0);

    var rect = svg.append('rect')
      .attr('width', width)
      .attr('height', height)
      .attr("x", 0)
      .attr("y", 0)
      .attr('fill', "url(#minimap_img)");

    return svg;
}

var crosscount = function(series){
    var counts = {};
    series.map(function(point){
        if(!counts.hasOwnProperty(point.x)){
            counts[point.x] = {};
        }
        if(!counts[point.x].hasOwnProperty(point.y)){
            counts[point.x][point.y] = 0;
        }
        counts[point.x][point.y] += 1;
    });
    var answers = [];
    Object.getOwnPropertyNames(counts).map(function(idx){
        Object.getOwnPropertyNames(counts[idx]).map(function(idy){
            answers.push({
                x: parseInt(idx),
                y: parseInt(idy),
                ct: counts[idx][idy]
            });
        });
    });
    return answers;
}

var stat_card = function(shard, destination, params){

  var struct = {};
  var urls = [
    $.getJSON(utils.parse_urls.url_for(shard, 'allstate', 'statelog'))
  ];

  // Get the replay parse info
  Promise.all(urls).then(function(data){
    data = data[0];
    data.map(function(item){
      var time = item['offset_time'];
      struct[String(time)] = item;
    });

  }).then(function(items){
    var rawTemplate = `<div class="statcard {{css_classes}} {{lifestate}}">
    <div>
    <i class='d2mh {{hero_css}}'></i>
      <div style='float:right'>
      <div><text>{{kills}} / {{deaths}} / {{assists}}</text></div>
      <div><text>{{last_hits}} / {{denies}}</text></div>
      </div>
    </div>
          <div class="stats">
            <div class="css-progress-bar horizontal health">
              <div class="css-progress-track">
                <div class="css-progress-fill" style='width:{{health_pct}}%; float:left; background: green;'>
                  <span class='bar-nums'>{{health}} / {{max_health}}</span>
                </div>
              </div>
            </div>
            <div class='mana'>
            <div class="css-progress-bar horizontal mana">
              <div class="css-progress-track">
                <div class="css-progress-fill" style='width:{{mana_pct}}%; float:left; background: blue;'>
                  <span class='bar-nums'>{{mana}} / {{max_mana}}</span>
                </div>
              </div>
            </div>
           </div>
           <div class='strength'>
             Str: {{strength}} + {{strength_add}} = {{strength_total}}
           </div>
           <div class='intelligence'>
             Int: {{intelligence}} + {{intelligence_add}} = {{intelligence_total}}
           </div>
           <div class='agility'>
             Agi: {{agility}} + {{agility_add}} = {{agility_total}}
           </div>
           <div class='damage'>
             Dmg: {{base_damage}} + {{bonus_damage}} = {{total_damage}}
           </div>
           <div class='gold'>
             Gold: {{unreliable_gold}} + {{reliable_gold}} = {{total_gold}}
           </div>
           <div class='total_gold'>
             Tot Gold: {{total_earned_gold}}
           </div>
            <div class='row' id='items' style='text-align:center'>
              <div class='col-md-12'>
                <div class='row'>
                 <div class='col-xs-1' id='item_0'>
                    <i class='d2items {{item_0}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_1'>
                    <i class='d2items {{item_1}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_2'>
                    <i class='d2items {{item_2}}'></i>
                  </div>
                </div>
              </div>
              <div class='col-md-12'>
                <div class='row'>
                  <div class='col-xs-1' id='item_3'>
                    <i class='d2items {{item_3}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_4'>
                    <i class='d2items {{item_4}}'></i>
                  </div>
                  <div class='col-xs-1' id='item_5'>
                    <i class='d2items {{item_5}}'></i>
                  </div>
                </div>
              </div>
            </div>

          </div>
        </div>`;
    var compiledTemplate = Handlebars.compile(rawTemplate); // (step 2)
    // Items health mana kda last hits denies
    var update = function(time){

      var context = {
        title: shard.name,
        css_classes: shard.css_classes,
      };

      if (struct[time]===undefined) {
        $(destination).html('Not defined');
      }else{
        for (var attrname in struct[String(time)]) {
          context[attrname] = struct[String(time)][attrname];
        }
      }


      context['strength_add'] = (context['strength_total'] - context['strength']).toFixed(0);

      context['lifestate'] = context['health'] > 0 ? 'alive' : 'dead';



      context['health_pct'] = ((context['health'] / context['max_health'])*100).toFixed(0);
      context['mana_pct'] = ((context['mana'] / context['max_mana'])*100).toFixed(0);

      context['agility_add'] = (context['agility_total'] - context['agility']).toFixed(0);

      context['intelligence_add'] = (context['intelligence_total'] - context['intelligence']).toFixed(0);

      context['hero_css'] = shard.hero_name;

      context['total_gold'] = (
        parseInt(context['unreliable_gold']) + parseInt(context['reliable_gold'])
      ).toFixed(2);

      [
        'agility',
        'agility_total',
        'strength',
        'strength_total',
        'intelligence',
        'intelligence_total',
        'health',
        'max_health',
        'mana',
        'max_mana',
      ].map(function(field){
        context[field] = context[field].toFixed(0);
      });

      ['item_0', 'item_1', 'item_2', 'item_3', 'item_4', 'item_5'].map(
        function(d){
        if (context[d] === null) {
          context[d] = 'emptyitembg';
        }else{
          context[d] = context[d].substring(5);
        }
      });

      var html = compiledTemplate(context);
      $(destination).html(html);

    }

    update(0);
    $(window).on('update', function(evt, arg){
      update(arg);
    })

  }).catch(function(e){
    console.log(e);
  })
};


var playback_shards = function(shards){

  var urls = shards.map(function(shard){
    var location = utils.parse_urls.url_for(shard, 'allstate', 'statelog');
    return $.getJSON(location);
  });
  var min;
  var max;
  var start = 0;

  // Get the replay parse info
  Promise.all(urls).then(function(data){
    min = d3.min(data, function(series){
      return d3.min(series, function(x){
        return x.offset_time
      })
    });
    max = d3.max(data, function(series){
      return d3.max(series, function(x){
        return x.offset_time
      })
    });
    window.jsUtils.playback(min, max, 1, utils.axis_format.pretty_times);
  }).catch(function(e){
    console.log(e);
  })




}

module.exports = {
  stat_lineup: stat_lineup,
  scatterline: scatterline,
  item_scatter: item_scatter,
  item_inventory: item_inventory,
  multifacet_lineup: multifacet_lineup,
  minimap: minimap,
  position_heatmap: position_heatmap,
  stat_card: stat_card,
  playback_shards: playback_shards
};


