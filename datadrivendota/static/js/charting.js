function smartTicks(d) {
    if ((d / 1000000) >= 1) {
        return d / 1000000 + "M";
    }
    if ((d / 1000) >= 1) {
        return d / 1000 + "K";
    }
    return d;
}

function convertToSlug(Text)
{
    return Text
        .toLowerCase()
        .replace(/ /g,'-')
        .replace(/[^\w-]+/g,'')
        ;
}

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    });
}

var getVals = function(obj){
   var vals = [];
   for(var key in obj){
      vals.push(obj[key]);
   }
   return vals;
}

function getColorScale(params){
  if ('color_range' in params && 'color_domain' in params) {
      var color = d3.scale.ordinal()
              .range(params.color_range)
              .domain(params.color_domain);
  }
  else {
      var color = d3.scale.category10();
  }

  return color;
}

function make_tooltip(){
    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);
    return div;
}

function linear_x_scale(params){
  var width = get_width(params);
  return d3.scale.linear()
        .domain([params['x_min'],params['x_max']])
        .range([0, width]);
}


function linear_y_scale(params){
  var height = get_height(params);
  return d3.scale.linear()
        .domain([params['y_min'], params['y_max']])
        .range([height,0]);
}

function inner_chart(params, svg){
  var width = get_width(params);
  var height = get_height(params);
  var margin = get_margin(params);
  var inner = svg.append("g");
  inner.attr("class", 'inner-chart')
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
  return inner;
}

function outer_chart(params, placement_div, data){
  var outerWidth = get_outer_width(params);
  var outerHeight = get_outer_height(params);
  var outer = d3.select(placement_div)
        .selectAll("svg")
        .data(data)
        .enter().append("svg:svg")
        .attr("width", outerWidth)
        .attr("height", outerHeight)
        .attr("class", 'outer-chart');
  return outer;
}

function draw_x_axis(params, g, xAxis){

  var height = get_height(params);
  var width = get_width(params);
  g.append("g")
      .attr("class", "x-axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .append("text")
        .attr("class", "x-axis-label")
        .attr("y", -16)
        .attr("x", width)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params['x_label']);
}

function draw_y_axis(params, g, yAxis){
  var height = get_height(params);
  var width = get_width(params);
  g.append("g")
    .attr("class", "y-axis")
    .attr("transform", "translate(0,0)")
    .call(yAxis)
    .append("text")
      .attr("class", "y-axis-label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(params['y_label']);

}

function draw_title(params, panels, svg){
    var outerWidth = get_outer_width(params);
    svg.append("g")
    .attr('class','chart-title-g')
    .attr("transform", "translate(0,0)")
    .append("text")
      .attr("x", outerWidth/2)
      .attr("dy", "1em")
      .attr("class", 'chart-title')
      .style("text-anchor", "middle")
      .text(function(d){
        return panels[d.key]['display_name'];
      });

}

function draw_legend(params, groups, svg, color){
  var outerWidth = get_outer_width(params);
  var outerHeight = get_outer_height(params);
  var margin = get_margin(params);
  var pctWidth = get_legend_width_pct(params);
  var pctHeight = get_legend_height_pct(params);
  var fadeOpacity = get_fade_opacity(params);

  var legend = svg.append("g");

  data = d3.nest()
    .key(function(d){return d.index;}).sortKeys(d3.ascending)
    .entries(groups);

  legend.attr("class", "legend")
        .attr("transform", "translate("
          +outerWidth*pctWidth+
          ","
          +outerHeight*pctHeight+")");

  var rows = legend.selectAll('rect')
        .data(function(d){return d.values;})
        .enter();

      rows.append("rect")
        .attr("x", 2)
        .attr("y", function(d, i){ return i *  20;})
        .attr("width", 10)
        .attr("height", 10)
        .attr("class", function(d) {return groups[d['key']]['class_selector']})
        .style("fill", function(d) {
           var return_color = groups[d['key']]['color'];
           return return_color;
        })
        .style('stroke-width',1)
        .style('stroke','#000000')
        .on("mouseover",
          function (d, i) {
            str = '.data-toggleable:not(.'+groups[d['key']]['class_selector']+')'
            d3.selectAll(str)
            .transition()
            .duration(1000)
            .style('opacity',fadeOpacity);
        })
        .on("mouseout", function(d) {
            d3.selectAll('.data-toggleable:not(.'+groups[d['key']]['class_selector']+')')
            .transition()
            .duration(1000)
            .style('opacity',1);
          }
        );

  rows.append('text')
    .attr("class", function(d){
      return 'legend-text '+String(groups[d['key']]['class_selector']);
    })
    .attr("x", 14)
    .attr("y", function(d, i){ return 11+(i *  20);})
    .text(function(d){
      return groups[d['key']]['display_name'];
    });
}

function draw_path(dataset, groups,  line, color, params){
    var path_stroke_width = get_path_stroke_width(params)
    dataset.append("svg:path")
    .attr("d", function(d){return(line(d.values));})
    .style("stroke", function(d) {
      return groups[d.values[0].group_var]['color'];
    })
    .style("stroke-width", path_stroke_width)
    .style("fill", 'none')
    .attr("class", function(d){
      return 'data-toggleable dataset lines '+d.values[0].classes.join(' ');
    });
}

function append_datasets(g, groups){
  return g.selectAll('.dataset')
  .data(function(d){return(d.values);})
  .enter()
  .append('g')
  .attr("class", function(d){
    return 'datagroup '+groups[d.values[0].group_var]['class_selector'];
  })
  .attr("id", function(d){return convertToSlug(d.key);});

}


function get_margin(params){
  return params.margin;
}

function get_padding(params){
  return params.padding;
}

function get_width(params){
  var padding = get_padding(params);
  return get_inner_width(params) - padding.left - padding.right;
}
function get_height(params){
  var padding = get_padding(params);
  return get_inner_height(params) - padding.top - padding.bottom;
}
function get_inner_width(params){
  var margin = get_margin(params);
  return get_outer_width(params) - margin.left - margin.right;
}
function get_inner_height(params){
  var margin = get_margin(params);
  return get_outer_height(params) - margin.top - margin.bottom;
}
function get_outer_width(params){
  return params.outerWidth;
}
function get_outer_height(params){
  return params.outerHeight;
}
function get_legend_width_pct(params){
  return params.legendWidthPercent;
}
function get_legend_height_pct(params){
  return params.legendHeightPercent;
}
function get_path_stroke_width(params){
  return params.path_stroke_width;
}
function get_fade_opacity(params){
  return params.fadeOpacity;
}

function draw_scatterplot(source, placement_div, callback){
    var raw_data = source['data'];
    var params = source['parameters'];
    var groups = source['groups'];
    var panels = source['panels'];
    data = d3.nest()
    .key(function(d){return d.panel_var;}).sortKeys(d3.ascending)
    .key(function(d){return d.group_var;}).sortKeys(d3.ascending)
    .entries(raw_data);

    var div = make_tooltip();

    var svg = outer_chart(params, placement_div, data);

    var line = d3.svg.line()
        .interpolate("linear")
        .x(function(d) { return x(d.x_var); })
        .y(function(d) { return y(d.y_var); });

    var x = linear_x_scale(params);
    var y = linear_y_scale(params);

    var xAxis = d3.svg.axis()
                .scale(x).orient("bottom")
                .tickFormat(function (d) {
                    if ((d / 1000) >= 1) {
                      d = d / 1000 + "K";
                    }
                    return d;
                }),
        yAxis = d3.svg.axis()
                .scale(y).orient("left")
                .tickFormat(function (d) {
                    if ((d / 1000) >= 1) {
                      d = d / 1000 + "K";
                    }
                    return d;
                })
                // .tickFormat(d3.format("d"));

    if (params.x_ticks) {xAxis = xAxis.ticks(params.x_ticks)};
    if (params.y_ticks) {yAxis = yAxis.ticks(params.y_ticks)};

    var color = getColorScale(params);

    var g = inner_chart(params, svg);

    draw_x_axis(params, g, xAxis);
    draw_y_axis(params, g, yAxis);
    draw_title(params, panels, svg);

    point_size_scale = d3.scale.linear()
      .domain([params['pointDomainMin'],params['pointDomainMax']])
      .range([params['pointSizeMin'],params['pointSizeMax']])
      .clamp(true);

    stroke_width_scale = d3.scale.linear()
      .domain([params['strokeDomainMin'],params['strokeDomainMax']])
      .range([params['strokeSizeMin'],params['strokeSizeMax']])
      .clamp(true);

    var dataset = append_datasets(g, groups)

    dataset.selectAll('.points')
      .data(function(d){return d.values;})
      .enter()
      .append("a").attr("xlink:href", function(d) {
        if(d.url){return d.url;} else {return '';}
      })
      .append('circle')
      .attr('cx',function(d){
        return(x(d.x_var));
      })
      .attr('cy',function(d){return(y(d.y_var)); })
      .attr("class", function(d){
          for(var key in d.classes){
            d.classes[key]=convertToSlug(d.classes[key]);
          }
          return 'data-toggleable dataset points '+d.classes.join(' ');
      })
      .attr('r', function(d){
        return(point_size_scale(d.point_size));
      })
      .attr('stroke-width', function(d){
        return(stroke_width_scale(d.stroke_width));
      })
      .style("fill", function(d) { return groups[d.group_var]['color']})
      .style("stroke", function(d) {
        return '#000000'
        // return color(String(d.group_var));
      })
      .on("mouseover", function(d) {
        div.transition()
          .duration(200)
          .style("opacity", 0.9);
        div .html(d.tooltip)
          .style("left", (d3.event.pageX) + "px")
          .style("top", (d3.event.pageY - 28) + "px");
        })
      .on("mouseout", function(d) {
          div.transition()
            .duration(500)
            .style("opacity", 0);
    });
    if(params['draw_path']){
      draw_path(dataset, groups, line, color, params);
    }

    if(params['draw_legend']){
      draw_legend(params, groups, svg, color);
    }
    if (typeof callback === 'function'){
      callback();
    }

}
function draw_barplot(source, placement_div, callback){
  var raw_data = source['data'];
  var params = source['parameters'];
  var groups = source['groups'];
  var panels = source['panels'];

  var width = get_width(params),
      height = get_height(params);

  data = d3.nest()
  .key(function(d){return d.panel_var;})
  .key(function(d){return d.group_var;})
  .entries(raw_data);

  var div = make_tooltip();
  var svg = outer_chart(params, placement_div, data);

  var x = d3.scale.ordinal()
    .rangeRoundBands([0, width], 0.1)
    .domain(params.x_set);
  var y = linear_y_scale(params);
  var xAxis = d3.svg.axis().scale(x).orient("bottom")
              .tickValues(params.tick_values)
  if (params.x_ticks) {xAxis = xAxis.ticks(params.x_ticks)};
  var yAxis = d3.svg.axis()
    .scale(y)
    .orient("left")
    .tickFormat(function (d) {
                    if ((d / 1000) >= 1) {
                      d = d / 1000 + "K";
                    }
                    return d;
                })
  if (params.y_ticks) {yAxis = yAxis.ticks(params.y_ticks)};

  var color = getColorScale(params);
  var g = inner_chart(params, svg);

  draw_title(params, panels, svg);

  g.append("g")
      .attr("class", "x-axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .selectAll("text")
          .style("text-anchor", "end")
          .attr("dx", "-1em")
          .attr("dy", "-0.3em")
          .attr("transform", function(d) {
              return "rotate(-90)";
              })
      .append("text")
        .attr("y", -16)
        .attr("x", width)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params['x_label']);

  draw_y_axis(params, g, yAxis);

  var dataset = append_datasets(g, groups)


  dataset.selectAll('.bars')
      .data(function(d){return d.values;}).enter()
      .append("a")
      .attr("xlink:href", function(d) {
        if(d.url){return d.url;}
        else {return '';}
      })
  .append('rect')
  .attr("class", function(d){
        for(var key in d.classes){
          d.classes[key]=convertToSlug(d.classes[key]);
        }
        return 'data-toggleable dataset points '+d.classes.join(' ');
    })
  .attr("x", function(d) { return x(d.x_var); })
  .attr("width", x.rangeBand())
  .attr("y", function(d) { return y(d.y_var); })
  .attr("height", function(d) { return height - y(d.y_var); })
  .style("fill", function(d) { return groups[d.group_var]['color'];})
  .style('stroke-width', 1)
  .style('stroke','#000000')

  .on("mouseover", function(d) {

          div.transition()
            .duration(200)
            .style("opacity", 0.9);

          div.html(d.tooltip)
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px")

          })
      .on("mouseout", function(d) {
          div.transition()
              .duration(500)
              .style("opacity", 0);
      });

  if(params['draw_legend']){
    draw_legend(params, groups, svg, color);
  }
  if (typeof callback === 'function'){
    callback();
  }

}


function draw_scatterseries(source, placement_div, callback){
  var raw_data = source['data'];
  var params = source['parameters'];
  var groups = source['groups'];
  var panels = source['panels'];
  params['draw_path'] = 'True';

  data = d3.nest()
  .key(function(d){return d.panel_var;})
  .key(function(d){return d.group_var;})
  .key(function(d){return d.series_var;})
  .entries(raw_data);

  var div = make_tooltip();

  var svg = outer_chart(params, placement_div, data);

  var line = d3.svg.line()
      .interpolate("linear")
      .x(function(d) { return x(d.x_var); })
      .y(function(d) { return y(d.y_var); });


  var x = linear_x_scale(params);
  var y = linear_y_scale(params);

  var xAxis = d3.svg.axis().scale(x).orient("bottom"),
      yAxis = d3.svg
        .axis()
        .scale(y)
        .orient("left")
        .tickFormat(function (d) {
                    if ((d / 1000) >= 1) {
                      d = d / 1000 + "K";
                    }
                    return d;
                });

  if (params.x_ticks) {xAxis = xAxis.ticks(params.x_ticks)};
  if (params.y_ticks) {yAxis = yAxis.ticks(params.y_ticks)};

  var color = getColorScale(params);

  var g = inner_chart(params, svg);

  draw_x_axis(params, g, xAxis);
  draw_y_axis(params, g, yAxis);

  draw_title(params, panels, svg);

  var datagroups = g.selectAll('.groups').data(function(d){
          return(d.values);
      }).enter().append('g')
  .attr("class", 'group')
  .attr("id", function(d){return convertToSlug(d.key);});


  var dataset = datagroups.selectAll('.dataset')
    .data(function(d){return d.values;})
    .enter()
    .append("g")
    .attr("class", function(d){
      return '';//data-toggleable'
      // return 'datagroup '+groups[d.values[0].group_var]['class_selector'];
    })
    .attr("id", function(d){return d.key;});

  dataset.selectAll('.points').data(function(d){
        return d.values;}
      ).enter()
      .append('a')
      .attr("xlink:href", function(d) {
        if(d.url){return d.url;} else {return '';}
      })
      .append('circle')
      .attr('cx',function(d){return(x(d.x_var)); })
      .attr("class", function(d){
          for(var key in d.classes){
            d.classes[key]=convertToSlug(d.classes[key]);
          }
          return 'data-toggleable dataset points '+d.classes.join(' ');
      })
      .attr('cy',function(d){return(y(d.y_var)); })
      .attr('r', 1)
      .style("fill", function(d) { return color(String(d.group_var));})
      .on("mouseover", function(d) {
        div.transition()
            .duration(200)
            .style("opacity", 0.9);
        div .html(d.tooltip)
            .style("left", (d3.event.pageX) + "px")
            .style("top", (d3.event.pageY - 28) + "px");
        }
      )
      .on("mouseout", function(d) {
          div.transition()
              .duration(500)
              .style("opacity", 0);
      });

  if(params['draw_path']){
    draw_path(dataset, groups, line, color, params);
  }

  if(params['draw_legend']){
    draw_legend(params, groups, svg, color);
  }
  if (typeof callback === 'function'){
    callback();
  }

}

function hero_dot_plot(
  chart_json,
  margin,
  x_var,
  x_label,
  y_var,
  y_label,
  placement_div,
  autostart,
  button_controller
  ){

   if(typeof(autostart)==='undefined') autostart = false;
   if(typeof(button_controller)==='undefined') button_controller = false;

  var padding = {top: 0, right: 0, bottom: 0, left: 0},
      outerWidth = 300,
      outerHeight = 300,
      innerWidth = outerWidth - margin.left - margin.right,
      innerHeight = outerHeight - margin.top - margin.bottom;
      width = innerWidth - padding.left - padding.right,
      height = innerHeight - padding.top - padding.bottom;

  var transitionDelay = 500
  var x_min = d3.min(
          chart_json,
          function(d){
              return(d3.min(d['data'], function(p){
                  return(p[x_var])
              }))
          });
  var y_min = d3.min(
          chart_json,
          function(d){
              return(d3.min(d['data'], function(p){
                  return(p[y_var])
              }))
          });
  var x_max = d3.max(
          chart_json,
          function(d){
              return(d3.max(d['data'], function(p){
                  return(p[x_var])
              }))
          });
  var y_max = d3.max(
          chart_json,
          function(d){
              return(d3.max(d['data'], function(p){
                  return(p[y_var])
              }))
          });

  function toTitleCase(str)
  {
      temp = str.replace('npc_dota_hero_', ' ')
      temp = temp.replace('_', ' ')
      return temp.replace('_', ' ').replace(/\w\S*/g, function(txt){return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();});
  }

  var x = d3.scale.linear()
      .range([0, width])
      .domain([x_min, x_max]);

  var y = d3.scale.linear()
      .range([height, 0])
      .domain([y_min, y_max]);

  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .ticks(6)

  var yAxis = d3.svg.axis()
      .scale(y)
      .orient("left")
  if (y_max >= 1000){
      yAxis.tickFormat(function (d) {
          strng = String(d/1000)+'K'
          return strng;
      });
  }

  var line = d3.svg.line()
      .x(function(d){
          return x(d[x_var])
      })
      .y(function(d){
          return y(d[y_var])
      });

  var div = d3.select("body").append("div")
      .attr("class", "tooltip")
      .style("opacity", 0);


  inner_svg = d3.select(placement_div).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .attr("class", 'outer-chart')
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
      .attr("class", 'inner-chart')

  //Draw X
  inner_svg.append("g")
      .attr("class", "x-axis")
      .attr("transform", "translate(0," + height + ")")
      .call(xAxis)
      .append("text")
      .attr("class", "x-axis-label")
      .attr("y", -16)
      .attr("x", width)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(x_label);

  //Draw Y
  inner_svg.append("g")
      .attr("class", "y-axis")
      .attr("transform", "translate(0,0)")
      .call(yAxis)
      .append("text")
      .attr("class", "y-axis-label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(y_label);

  inner_svg.selectAll('.series')
      .data(chart_json)
      .enter()
      .append('circle')
      .attr('cx',function(d){
          return(x(d['data'][0][x_var]));
      })
      .attr('cy',function(d){
          return(y(d['data'][0][y_var]));
      })
      .attr('r', function(d){
          return(5);
      })
      .style("stroke", function(d) {return('#000000');})
      .attr("class", function(d){return(d['name'])})
      .on("mouseover", function(d) {
      div.transition()
          .duration(200)
          .style("opacity", 0.9);

          div.html(toTitleCase(d.name))
          .style("left", (d3.event.pageX) + "px")
          .style("top", (d3.event.pageY - 28) + "px");
      })
      .on("mouseout", function(d) {
          div.transition()
          .duration(500)
          .style("opacity", 0);
      });


      var idx = 0
      var duration = 100
      var max_len = chart_json[0]['data'].length
      var update = function () {
          if(idx>=max_len){
              stop()
              idx=0
          }
          if(idx<0){
              stop()
              idx=max_len-1
          }

          updateTimer(chart_json[0]['data'][idx]['time'])

          d3.selectAll(placement_div+' circle')
              .transition()
              .ease('linear')
              .duration(duration)
              .attr('cx',function(d){
                  return(x(d['data'][idx][x_var]));
              })
              .attr('cy',function(d){
                  return(y(d['data'][idx][y_var]));
              })
      }

      var tick = function(){
          ++idx
          start()
      }

      var myhandle
      var start = function(){
          update()
          myhandle = setTimeout(tick, duration)
      }

      var stop = function (){
          clearTimeout(myhandle)
      }

      $('#start-animation').on("click", function(){
        if(button_controller){
          $('#start-animation').toggle();
          $('#stop-animation').toggle();
          $('#back-animation').toggle();
          $('#forward-animation').toggle();
        }

          start();
      });

      $('#stop-animation').on("click", function(){
        if(button_controller){
          $('#start-animation').toggle();
          $('#stop-animation').toggle();
          $('#back-animation').toggle();
          $('#forward-animation').toggle();
        }
          stop();
      });
      $('#back-animation').on("click", function(){
          --idx
          update();
      });
      $('#forward-animation').on("click", function(){
          ++idx
          update();
      });
      if(autostart){
        start();
      }

}

function side_progess_plot(
    chart_json,
    x_var,
    x_label,
    y_var,
    y_label,
    placement_div,
    margin,
    slider_name,
    button_controller
    ){


    if(typeof(button_controller)==='undefined') button_controller = false;

    var padding = {top: 0, right: 0, bottom: 0, left: 0},
        outerWidth = 300,
        outerHeight = 300,
        innerWidth = outerWidth - margin.left - margin.right,
        innerHeight = outerHeight - margin.top - margin.bottom,
        width = innerWidth - padding.left - padding.right,
        height = innerHeight - padding.top - padding.bottom;

    var x_min = d3.min(
            chart_json,
            function(d){
                return(d3.min(d['data'], function(p){
                    return(p[x_var])
                }))
            });
    var y_min = d3.min(
            chart_json,
            function(d){
                return(d3.min(d['data'], function(p){
                    return(p[y_var])
                }))
            });
    var x_max = d3.max(
            chart_json,
            function(d){
                return(d3.max(d['data'], function(p){
                    return(p[x_var])
                }))
            });
    var y_max = d3.max(
            chart_json,
            function(d){
                return(d3.max(d['data'], function(p){
                    return(p[y_var])
                }))
            });

    var x = d3.scale.linear()
        .range([0, width])
        .domain([x_min, x_max]);

    var y = d3.scale.linear()
        .range([height, 0])
        .domain([y_min, y_max]);

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(4)
        .tickFormat(function (d) {
            strng = String((d-d%60)/60)+':'+String(d%60)
            return strng;
        });

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left")
    if (y_max >= 1000){
        yAxis.tickFormat(function (d) {
            strng = String(d/1000)+'K'
            return strng;
        });
    }

    var line = d3.svg.line()
        .x(function(d){
            return x(d[x_var])
        })
        .y(function(d){
            return y(d[y_var])
        });

    inner_svg = d3.select(placement_div).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .attr("class", 'outer-chart')
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")")
        .attr("class", 'inner-chart')

    //Draw X
    inner_svg.append("g")
        .attr("class", "x-axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
        .attr("class", "x-axis-label")
        .attr("y", -16)
        .attr("x", width)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(x_label);

    //Draw Y
    inner_svg.append("g")
        .attr("class", "y-axis")
        .attr("transform", "translate(0,0)")
        .call(yAxis)
        .append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(y_label);

    inner_svg.selectAll('.series')
        .data(chart_json)
        .enter()
        .append('g')
        .append("svg:path")
        .attr("d", function(d){
            return(line(d['data']));
        })
        .style("stroke-width", 2)
        .style("stroke", function(d) {
          return(d['color']);
        })

    inner_svg.append('g')
        .append("rect")
        .attr("x", x(x_min))
        .attr("y", y(y_max))
        .attr("width", 3)
        .attr("height", height+2)
        .attr("class", slider_name)

    var idx = 0
    var duration = 100
    var max_len = chart_json[0]['data'].length

    var update = function () {
        if(idx>=max_len){
            stop()
            idx=0
        }
        if(idx<0){
            stop()
            idx=max_len-1
        }

        updateTimer(chart_json[0]['data'][idx]['time'])

         d3.selectAll('.'+slider_name)
        .transition()
        .duration(duration)
        .attr('x', function(){
            return x(chart_json[0]['data'][idx]['time'])
        });
    }

    var tick = function(){
        ++idx;
        start()
    }

    var myhandle
    var start = function(){
        update()
        myhandle = setTimeout(tick, duration)
    }

    var stop = function (){
        clearTimeout(myhandle)
    }

    $('#start-animation').on("click", function(){
        if(button_controller){
          $('#start-animation').toggle();
          $('#stop-animation').toggle();
          $('#back-animation').toggle();
          $('#forward-animation').toggle();
        }
        start();
    });

    $('#stop-animation').on("click", function(){
        if(button_controller){
          $('#start-animation').toggle();
          $('#stop-animation').toggle();
          $('#back-animation').toggle();
          $('#forward-animation').toggle();
        }
        stop();
    });
    $('#back-animation').on("click", function(){
        --idx;
        update();
    });
    $('#forward-animation').on("click", function(){
        ++idx;
        update();
    });

}


function updateTimer(d){
    $('#time-display').val(String((d-d%60)/60)+':'+String(d%60))
}



function plot(source, div, callback){
    if(source.parameters['chart']=='xyplot'){
        draw_scatterplot(source, div, callback);
    }
    else if(source.parameters['chart']=='barplot'){
        draw_barplot(source, div, callback);
    }
    else if(source.parameters['chart']=='scatterseries'){
        draw_scatterseries(source, div, callback);
    }

}
window.d3ening = {};
window.d3ening.plot = plot;
window.d3ening.hero_dot_plot = hero_dot_plot;
window.d3ening.side_progess_plot = side_progess_plot;

window.chartUtils = {}
window.chartUtils.convertToSlug = convertToSlug
window.chartUtils.toTitleCase = toTitleCase
window.chartUtils.make_tooltip = make_tooltip


var new_index = function(dataset, i){
  if(i==dataset.length){
    return(0);
  }
  else{
    return(i+1)
  }
}

var side_progress_line = function(dataset, target_selector, bind_button, params, callback){

  initial_fract = 3
  var initial_count = Math.round(dataset.length/initial_fract);

  var margin = {top: 15, right: 15, bottom: 25, left: 60},
      width = params.width - margin.right,
      height = params.height - margin.top - margin.bottom;

  data_slice = dataset.slice(0, initial_count)

  var x = d3.scale.linear()
      .domain([
        d3.min(data_slice, function(d){return(d['times'])}),
        d3.max(data_slice, function(d){return(d['times'])}),
      ])
      .range([0, width]);

  var y = d3.scale.linear()
      .domain([
        d3.min(data_slice, function(d){return(
          Math.min(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        }),
        d3.max(data_slice, function(d){return(
          Math.max(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        })
      ])
      .range([height, 0]);

  var radiantline = d3.svg.line()
      .interpolate("basis")
      .x(function(d, i) { return x(d['times']); })
      .y(function(d, i) { return y(d['radiant']); });
  var direline = d3.svg.line()
      .interpolate("basis")
      .x(function(d, i) { return x(d['times']); })
      .y(function(d, i) { return y(d['dire']); });
  var diffline = d3.svg.line()
      .interpolate("basis")
      .x(function(d, i) { return x(d['times']); })
      .y(function(d, i) { return y(d['difference']); });

  var svg = d3.select(target_selector).append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .style("margin-left", -margin.left + "px")
      .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  svg.append("defs").append("clipPath")
      .attr("id", "clip")
      .append("rect")
      .attr("width", width)
      .attr("height", height);



  var xaxis = svg.append("g")
      .attr("class", "x axis")
      .attr("transform", "translate(0," + height + ")")
      .call(
        x.axis = d3.svg.axis().scale(x).orient("bottom").tickFormat(
          function(d,i){
            return(secondstotime(d))
          }
        )
      );

      xaxis.append("text")
        .attr("class", "x-axis-label")
        .attr("y", -16)
        .attr("x", width)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params.x_lab);


  var yaxis = svg.append("g")
      .attr("class", "y axis")
      .attr("transform", "translate(0,0)")
      .call(y.axis = d3.svg.axis().scale(y).orient("left"));

      yaxis.append("text")
      .attr("class", "y-axis-label")
      .attr("transform", "rotate(-90)")
      .attr("y", 6)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(params.y_lab);


  var radiant_path = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .append("svg:path")
      .data([data_slice])
      .attr("class", "radiant-line progress-line")

  var dire_path = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .append("svg:path")
      .data([data_slice])
      .attr("class", "dire-line progress-line")

  var diff_path = svg.append("g")
      .attr("clip-path", "url(#clip)")
      .append("svg:path")
      .data([data_slice])
      .attr("class", "difference-line progress-line")

  idx = initial_count;


  ;(function(idx, diff_path, dire_path, radiant_path, yaxis, xaxis, svg, diffline, direline, radiantline, x, y, margin, width, height, data_slice){
  function tick(dataset, idx, target_selector) {
    idx = new_index(dataset, idx)
    if(idx<dataset.length){
      data_slice.push(dataset[idx])
    }else{
      return
    }

    // update the domains
    x.domain([
      d3.min(data_slice, function(d){return(d['times'])}),
      d3.max(data_slice, function(d){return(d['times'])}),
    ]);
    y.domain([
        d3.min(data_slice, function(d){return(
          Math.min(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        }),
        d3.max(data_slice, function(d){return(
          Math.max(
            d['radiant'],
            d['dire'],
            d['difference']
            )
          )
        })
    ])


    // redraw the line
    svg.select(target_selector+" .radiant-line")
        .attr("d", radiantline)
        .attr("transform", null);
    svg.select(target_selector+" .dire-line")
        .attr("d", direline)
        .attr("transform", null);
    svg.select(target_selector+" .difference-line")
        .attr("d", diffline)
        .attr("transform", null);

    // // slide the x-axis left
    xaxis.transition()
        .duration(duration)
        .ease("linear")
        .call(x.axis);

    // // move the y axis
    yaxis.transition()
        .duration(duration)
        .ease("linear")
        .call(y.axis)
        .each("end", function(){tick(dataset, idx, target_selector)});


    // // pop the old data point off the front
    data_slice.shift();
  }
  $(bind_button).click(function(){
    tick(dataset, idx, target_selector);
  })

}(idx, diff_path, dire_path, radiant_path, yaxis, xaxis, svg, diffline, direline, radiantline, x, y, margin, width, height, data_slice))

  // if(typeof callback === 'undefined'){
  //   callback()
  // }
}
window.side_progress_line = side_progress_line

var side_progress_plot = function(url, params){
  $.getJSON(url, function(data){
    duration = params.duration;
    dataset = [];
    keys = Object.keys(data);
    for(i=0; i<data['times'].length;i++){
        data_obj = {}
        for(var key_idx in keys){
            data_obj[keys[key_idx]] = data[keys[key_idx]][i]
        }
        dataset.push(data_obj)
    }
    side_progress_line(dataset, 'div#body', '.magicbutton', params)
  })
}
window.side_progress_plot = side_progress_plot

var miniMap = function(heroes, state, timeslice, params){

    var selector = 'div#minimap'
    var width = $(selector).width()
    var height = width
    var building_initials = [
      {'y': 87, 'x': 78, 'id': 'npc_dota_goodguys_fort'},
      {'y': 78, 'x': 96, 'id': 'npc_dota_goodguys_melee_rax_bot'},
      {'y': 96, 'x': 90, 'id': 'npc_dota_goodguys_melee_rax_mid'},
      {'y': 105, 'x': 78, 'id': 'npc_dota_goodguys_melee_rax_top'},
      {'y': 81, 'x': 96, 'id': 'npc_dota_goodguys_range_rax_bot'},
      {'y': 99, 'x': 87, 'id': 'npc_dota_goodguys_range_rax_mid'},
      {'y': 105, 'x': 72, 'id': 'npc_dota_goodguys_range_rax_top'},
      {'y': 84, 'x': 168, 'id': 'npc_dota_goodguys_tower1_bot'},
      {'y': 123, 'x': 117, 'id': 'npc_dota_goodguys_tower1_mid'},
      {'y': 153, 'x': 75, 'id': 'npc_dota_goodguys_tower1_top'},
      {'y': 78, 'x': 123, 'id': 'npc_dota_goodguys_tower2_bot'},
      {'y': 108, 'x': 99, 'id': 'npc_dota_goodguys_tower2_mid'},
      {'y': 122, 'x': 75, 'id': 'npc_dota_goodguys_tower2_top'},
      {'y': 80, 'x': 98, 'id': 'npc_dota_goodguys_tower3_bot'},
      {'y': 99, 'x': 91, 'id': 'npc_dota_goodguys_tower3_mid'},
      {'y': 108, 'x': 75, 'id': 'npc_dota_goodguys_tower3_top'},
      {'y': 90, 'x': 81, 'id': 'npc_dota_goodguys_tower4'},
      {'y': 174, 'x': 171, 'id': 'npc_dota_badguys_fort'},
      {'y': 162, 'x': 180, 'id': 'npc_dota_badguys_melee_rax_bot'},
      {'y': 167, 'x': 162, 'id': 'npc_dota_badguys_melee_rax_mid'},
      {'y': 185, 'x': 158, 'id': 'npc_dota_badguys_melee_rax_top'},
      {'y': 162, 'x': 177, 'id': 'npc_dota_badguys_range_rax_bot'},
      {'y': 168, 'x': 160, 'id': 'npc_dota_badguys_range_rax_mid'},
      {'y': 187, 'x': 158, 'id': 'npc_dota_badguys_range_rax_top'},
      {'y': 114, 'x': 178, 'id': 'npc_dota_badguys_tower1_bot'},
      {'y': 138, 'x': 136, 'id': 'npc_dota_badguys_tower1_mid'},
      {'y': 186, 'x': 84, 'id': 'npc_dota_badguys_tower1_top'},
      {'y': 141, 'x': 178, 'id': 'npc_dota_badguys_tower2_bot'},
      {'y': 156, 'x': 150, 'id': 'npc_dota_badguys_tower2_mid'},
      {'y': 186, 'x': 132, 'id': 'npc_dota_badguys_tower2_top'},
      {'y': 159, 'x': 178, 'id': 'npc_dota_badguys_tower3_bot'},
      {'y': 166, 'x': 160, 'id': 'npc_dota_badguys_tower3_mid'},
      {'y': 186, 'x': 155, 'id': 'npc_dota_badguys_tower3_top'},
      {'y': 172, 'x': 169, 'id': 'npc_dota_badguys_tower4'}
    ]

    d3.select(selector).style('position', 'relative')
    var svg = d3.select(selector)
        .append('svg')
        .attr('class', 'testchart')
        .attr('width', width)
        .attr('height', height)

    var defs = svg.append('svg:defs');

    defs.append('svg:pattern')
        .attr('id', 'tile-ww')
        .attr('patternUnits', 'userSpaceOnUse')
        .attr('width', width)
        .attr('height', height)
        .append('svg:image')
        .attr('xlink:href', 'https://s3.amazonaws.com/datadrivendota/images/minimap.png')
        .attr('x', 0)
        .attr('y', 0)
        .attr('width', width)
        .attr('height', height)

    svg.append("rect")
       .attr("fill", "url(#tile-ww)")
       .attr('width', width)
       .attr('height', height)
       .attr('x', 0)
       .attr('y', 0)

    function transX(xVal){
        presumed_min = 71
        scalar = minmax['x']['max'] - presumed_min
        xVal = xVal - 71
        return  20+(260*(xVal/scalar))
    }
    function transY(yVal){
        presumed_min = 71
        scalar = minmax['y']['max'] - presumed_min
        yVal = yVal - 71
        return  20+(yVal/scalar*240)
    }

    svg.selectAll('circle.observers')
      .data(state['Observers'])
      .enter()
      .append("circle")
      .attr('class', 'observers')
      .attr('r', 3)
      .attr('cy', function(d){return height-transY(d.y)+'px'})
      .attr('cx', function(d){return transX(d.x)+'px'})

    svg.selectAll('rect.sentries')
        .data(state['Sentries'])
        .enter()
        .append("rect")
        .attr('class', 'sentries')
        .attr('width', 4)
        .attr('height', 4)
        .attr('y', function(d){return height-transY(d.y)+'px'})
        .attr('x', function(d){return transX(d.x)+'px'})

    svg.selectAll('rect.buildings')
        .data(building_initials)
        .enter()
        .append("rect")
        .attr('class', function(d){return 'buildings '+d.id})
        .attr('width', 4)
        .attr('height', 4)
        .attr('data-coord',  function(d){return d.y})
        .attr('y', function(d){return height-transY(d.y)+'px'})
        .attr('x', function(d){return transX(d.x)+'px'})

    $.each(timeslice, function(idx, val){

        var icon_class = 'd2mh '+ heroes[idx]['name']
        var hero_icon = d3.select(selector).insert("i")
           .attr('class', icon_class)
           .style('position', 'absolute')
           .attr('width', 32)
           .attr('height', 32)
           .style('bottom', transY(val.y)+'px')
           .style('left', transX(val.x)+'px')

        // Listen for the update
        $(document).on('update', function(e, snapshot){
            icon_class = selector+' .d2mh.'+ heroes[idx]['name']
            d3.select(icon_class).transition().duration(params.interval_duration)
                .style('bottom', transY(snapshot[idx].y)+'px')
                .style('left', transX(snapshot[idx].x)+'px')
        })

    })

    $(document).on('update', function(e, snapshot, state){
        var circles = svg.selectAll('circle.observers')
        .data(state['Observers']);

        circles
        .transition()
        .duration(0)
        .attr('cy', function(d){return height-transY(d.y)+'px'})
        .attr('cx', function(d){return transX(d.x)+'px'});

        circles.enter()
        .append("circle")
        .attr('class', 'observers')
        .attr('r', 3)
        .attr('cy', function(d){return height-transY(d.y)+'px'})
        .attr('cx', function(d){return transX(d.x)+'px'})

        circles.exit().remove();


        var squares = svg.selectAll('rect.sentries')
        .data(state['Sentries']);

        squares
        .transition()
        .duration(0)
        .attr('y', function(d){return height-transY(d.y)+'px'})
        .attr('x', function(d){return transX(d.x)+'px'});

        squares.enter()
        .append("rect")
        .attr('class', 'sentries')
        .attr('width', 4)
        .attr('height', 4)
        .attr('y', function(d){return height-transY(d.y)+'px'})
        .attr('x', function(d){return transX(d.x)+'px'})

        squares.exit().remove();

        var building_temp = building_initials.filter(function(v){
          return $.inArray(v['id'], state['Buildings'])>=0;
        })

        var buildings = svg.selectAll('rect.buildings')
        .data(building_temp, function(d){return d.id});

        buildings.enter()
        .append("rect")
        .attr('class', function(d){return 'buildings '+d.id})
        .attr('width', 4)
        .attr('height', 4)
        .attr('y', function(d){return height-transY(d.y)+'px'})
        .attr('x', function(d){return transX(d.x)+'px'})

        buildings.exit().remove()


    })
}
 window.miniMap = miniMap

var statBars = function(heroes, timeslice, minmax, target, params){
    var selector = target
    var width = $(selector).width()
    var height = $(selector).height()
    params['width'] = width
    params['height'] = 292
    var margin = {top: 15, right: 15, bottom: 25, left: 60},
        width = params.width - margin.right - margin.left,
        height = params.height - margin.top - margin.bottom;


    var num_series = 3
    var num_heroes = 10

    bar_domain = []
    $.each(heroes, function(i,v){
        bar_domain.push(v['hero_name'])
    })

    var x0 = d3.scale.ordinal()
        .domain(bar_domain)
        .rangeBands([0, width], .2)

    var x1 = d3.scale.ordinal()
        .domain(['str', 'int', 'agi'])
        .rangeBands([0, x0.rangeBand()]);

    var ymax = d3.max(timeslice, function(d){
        return Math.max(
            d['str_total'],
            d['int_total'],
            d['agi_total']
        )
    });
    y_domain = [0, ymax];
    var y = d3.scale.linear()
        .domain(y_domain)
        .range(
            [height, 0]
        );

    var svg = d3.select(selector).insert('svg')
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var xAxis = svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', 'translate(0,'+height+')')
        .call(d3.svg.axis().scale(x0).orient('bottom'))

    xAxis.selectAll('text')
            .style('text-anchor', 'end')
            .attr('dx', '-1em')
            .attr('dy', '-0.3em')
            .attr('transform', function(d){
                return 'rotate(90)';
            })
        .append('text')
            .attr('y', -16)
            .attr('x', width)
            .attr('dy', '.71em')
            .style('text-anchor', 'end')
            .text(params['x_label'])

    var yAxis = svg.append('g').attr('class', 'y axis')
        .attr('transform', 'translate(0,0)')
        .call(
            y.axis = d3.svg.axis().scale(y)
            .orient('left').tickFormat(smartTicks)
        )

    yAxis.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params['y_label']);

    // Put minimap hero icons on bars
    d3.select(selector).style('position', 'relative')
    $.each(timeslice, function(idx, val){
        d3.select(selector)
            .append('i')
            .attr('class', 'd2mh '+heroes[val.hero_idx]['name'])
            .style('position', 'absolute')
            .style("left", x0.rangeBand()/2+margin.left+x0(heroes[val.hero_idx]['hero_name'])+'px')
            .style("bottom", (height-y(0))+'px')
    })

    // Put bars in for each series
    $.each(['str', 'int', 'agi'], function(idx, val){
        stat = val+'_total'
        rect_select = selector+' rect.'+stat

        svg.selectAll(rect_select)
            .data(timeslice)
            .enter()
            .append('rect')
            .attr('x', function(d){
                name = heroes[d.hero_idx]['hero_name']
                return x1(val)+x0(name)
            })
            .attr('y', function(d){
                return height-y(d[stat])
            })
            .attr('width', function(d){
               return x1.rangeBand()
            })
            .attr('height', function(d){
               return y(d[stat])
            })
            .attr('class', function(d){
                name = heroes[d.hero_idx]['hero_name']

                return stat+' '+name
            })
    })

        // Listen for the update
        $(document).on('update', function(e, timeslice){

            ymax = Math.max(d3.max(timeslice, function(d){
                return Math.max(
                    d['str_total'],
                    d['int_total'],
                    d['agi_total']
                )
            }), ymax)
            y_domain = [0, ymax+5]
            y.domain(y_domain)

            yAxis.transition()
                .duration(params.interval_duration)
                .ease('linear')
                .call(y.axis)

            $.each(['str', 'int', 'agi'], function(idx, val){
                stat = val+'_total'
                rect_select = selector+' rect.'+stat

                svg.selectAll(rect_select)
                    .data(timeslice)
                    .attr('x', function(d){
                        name = heroes[d.hero_idx]['hero_name']
                        return x1(val)+x0(name)
                    })
                    .attr('y', function(d){
                        return y(d[stat])
                    })
                    .attr('width', function(d){
                       return x1.rangeBand()
                    })
                    .attr('height', function(d){
                       return height-y(d[stat])
                    })
            })
        })
}

window.statBars = statBars


var goldBars = function(heroes, timeslice, minmax, x_var, y_var, target, params){
    var selector = target
    var width = $(selector).width()
    var height = $(selector).height()
    params['width'] = width
    params['height'] = 292
    var margin = {top: 15, right: 15, bottom: 25, left: 60},
        width = params.width - margin.right - margin.left,
        height = params.height - margin.top - margin.bottom;


    bar_domain = []
    $.each(heroes, function(i,v){
        bar_domain.push(v['hero_name'])
    })
    var x = d3.scale.ordinal()
        .rangeRoundBands([0, width], 0.1).domain(bar_domain)

    var ymax = d3.max(timeslice, function(d){
        return d['reliable_gold']+d['unreliable_gold']
    })
    y_domain = [0, ymax]
    var y = d3.scale.linear()
        .domain(y_domain)
        .range(
            [height, 0]
        )

    var svg = d3.select(selector).insert('svg')
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var xAxis = svg.append('g')
        .attr('class', 'x-axis')
        .attr('transform', 'translate(0,'+height+')')
        .call(d3.svg.axis().scale(x).orient('bottom'))

    xAxis.selectAll('text')
            .style('text-anchor', 'end')
            .attr('dx', '-1em')
            .attr('dy', '-0.3em')
            .attr('transform', function(d){
                return 'rotate(90)';
            })
        .append('text')
            .attr('y', -16)
            .attr('x', width)
            .attr('dy', '.71em')
            .style('text-anchor', 'end')
            .text(params['x_label'])



    var yAxis = svg.append('g').attr('class', 'y axis')
        .attr('transform', 'translate(0,0)')
        .call(
            y.axis = d3.svg.axis().scale(y)
            .orient('left').tickFormat(smartTicks)
        )

    yAxis.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params['y_label']);

    // Put minimap hero icons on bars
    d3.select(selector).style('position', 'relative')
    $.each(timeslice, function(idx, val){
        d3.select(selector)
            .append('i')
            .attr('class', 'd2mh '+heroes[val.hero_idx]['name'])
            .style('position', 'absolute')
            .style("left", x.rangeBand()/2+margin.left+x(heroes[val.hero_idx]['hero_name'])+'px')
            .style("bottom", (height-y(0))+'px')
    })

    svg.selectAll(selector +' rect.reliable').data(timeslice)
        .enter().append("rect")
        .attr("x", function(d) {
            return x(heroes[d.hero_idx]['hero_name']);
        })
        .attr("width", x.rangeBand())
        .attr("y", function(d) { return y(d['reliable_gold']); })
        .attr("height", function(d) {
            return height - y(d['reliable_gold']);
        })
        .attr("class", function(d) {
             return heroes[d.hero_idx]['name']+' reliable';
        })
        .on("mouseover", function(d) {
            params.tooltip_div.transition()
              .duration(200)
              .style("opacity", 0.9);
            params.tooltip_div.html(heroes[d.hero_idx]['hero_name'] + ' Reliable Gold')
              .style("left", (d3.event.pageX) + "px")
              .style("top", (d3.event.pageY - 28) + "px");
            }
        )
        .on("mouseout", function(d) {
            params.tooltip_div.transition()
            .duration(500)
            .style("opacity", 0);
        });

    svg.selectAll(selector +' rect.unreliable').data(timeslice)
        .enter().append("rect")
        .attr("x", function(d) {
            return x(heroes[d.hero_idx]['hero_name']);
        })
        .attr("width", x.rangeBand())
        .attr("y", function(d) {
            return y(d['reliable_gold']+d['unreliable_gold']);
        })
        .attr("height", function(d) {
            return height - y(d['unreliable_gold']);
        })
        .attr("class", function(d) {
             return toTitleCase(heroes[d.hero_idx]['name'])+' unreliable';
        })
        .on("mouseover", function(d) {
            params.tooltip_div.transition()
              .duration(200)
              .style("opacity", 0.9);
            params.tooltip_div.html(toTitleCase(heroes[d.hero_idx]['hero_name']) + ' Unreliable Gold')
              .style("left", (d3.event.pageX) + "px")
              .style("top", (d3.event.pageY - 28) + "px");
            }
        )
        .on("mouseout", function(d) {
            params.tooltip_div.transition()
            .duration(500)
            .style("opacity", 0);
        });

        // Listen for the update
        $(document).on('update', function(e, timeslice){

            ymax = Math.max(d3.max(timeslice, function(d){
                return d['reliable_gold']+d['unreliable_gold']
            }), ymax)
            y_domain = [0, ymax]
            y.domain(y_domain)

            yAxis.transition()
                .duration(params.interval_duration)
                .ease('linear')
                .call(y.axis)

            svg.selectAll(selector +' rect.unreliable').data(timeslice)
                .transition()
                .duration(params.interval_duration)
                .attr("x", function(d) {
                    return x(heroes[d.hero_idx]['hero_name']);
                })
                .attr("width", x.rangeBand())
                .attr("y", function(d) {
                    return y(d['reliable_gold']+d['unreliable_gold']);
                })
                .attr("height", function(d) {
                    return height - y(d['unreliable_gold']);
                })
            svg.selectAll(selector +' rect.reliable').data(timeslice)
                .transition()
                .duration(params.interval_duration)
                .attr("x", function(d) {
                    return x(heroes[d.hero_idx]['hero_name']);
                })
                .attr("width", x.rangeBand())
                .attr("y", function(d) { return y(d['reliable_gold']); })
                .attr("height", function(d) {
                    return height - y(d['reliable_gold']);
                })

        })
}
window.goldBars = goldBars

var updatingScatter = function(heroes, timeslice, minmax, x_var, y_var, target,params){
    var selector = target
    var width = $(selector).width()
    var height = width // Mmm, squares
    params['width'] = width
    params['height'] = height
    var margin = {top: 15, right: 15, bottom: 25, left: 35},
        width = params.width - margin.right - margin.left,
        height = params.height - margin.top - margin.bottom;


    var x = d3.scale.linear()
        .domain([
                minmax[x_var]['min'],
                minmax[x_var]['max']
            ])
        .range(
            [0, width]
        )
    var y = d3.scale.linear()
        .domain([
                minmax[y_var]['min'],
                minmax[y_var]['max']
            ])
        .range(
            [height, 0]
        )

    var svg = d3.select(selector).insert('svg')
        // .attr('class', 'kill_dmg')
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        // .style("margin-left", -margin.left + "px")
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


    var xAxis = svg.append('g').attr('class', 'x axis')
        .attr('transform', 'translate(0,'+height+')')
        .call(
            d3.svg.axis().scale(x).orient("bottom")
            .tickFormat(smartTicks).ticks(5)
        )

    xAxis.append("text")
        .attr("class", "x-axis-label")
        .attr("y", -16)
        .attr("x", width)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params['x_label'])

    var yAxis = svg.append('g').attr('class', 'y axis')
        .attr('transform', 'translate(0,0)')
        .call(
            y.axis = d3.svg.axis().scale(y)
            .orient('left').tickFormat(smartTicks).ticks(5)
        )

    yAxis.append("text")
        .attr("class", "y-axis-label")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end")
        .text(params['y_label']);

    // Put hero icons on dots
    d3.select(selector).style('position', 'relative')
    $.each(timeslice, function(idx, val){
        d3.select(selector)
            .append('i')
            .attr('class', 'toggleface d2mh '+heroes[val.hero_idx]['name'])
            .style('position', 'absolute')
            .style("left", margin.left+x(val[x_var])+'px')
            .style("top", margin.top+y(val[y_var])+'px')
    })

    svg.selectAll(selector +' circle').data(timeslice)
        .enter().append("circle")
        .attr("cx", function(d) {
             return x(d[x_var]);
        })
        .attr("cy", function(d) {
             return y(d[y_var]);
        })
        .attr("class", function(d) {
             return heroes[d.hero_idx]['name'];
        })
        .attr("r", 3)
        .on("mouseover", function(d) {
            params.tooltip_div.transition()
              .duration(200)
              .style("opacity", 0.9);
            params.tooltip_div.html(toTitleCase(heroes[d.hero_idx]['hero_name'])
              .style("left", (d3.event.pageX) + "px")
              .style("top", (d3.event.pageY - 28) + "px");
            }
        )
        .on("mouseout", function(d) {
            params.tooltip_div.transition()
            .duration(500)
            .style("opacity", 0);
        });

        // Listen for the update
        $(document).on('update', function(e, timeslice){
            d3.selectAll(selector+' circle').data(timeslice)
            .transition()
            .duration(params.interval_duration)
            .attr("cx", function(d) {
               return x(d[x_var]);
            })
            .attr("cy", function(d) {
                 return y(d[y_var]);
            })

            //Move heroes on the dots
            $.each(timeslice, function(idx, val){
                hero_icon = selector+' i.toggleface.d2mh.'+heroes[val.hero_idx]['name']
                d3.select(hero_icon)
                    .transition()
                    .duration(params.interval_duration)
                    .style("left", margin.left+x(val[x_var])+'px')
                    .style("top", margin.top+y(val[y_var])+'px')
            })

        })
}

window.updatingScatter = updatingScatter


var healthBars = function(heroes, timeslice, params){
    var health_bar_height = 5

    $.each(heroes, function(idx, val){
        var selector = '.'+val['name']+'_slot'
        var width = $(selector).width()

        var svg = d3.select(selector).insert("svg", 'img')
        .attr("width", width)
        .attr("height", 2*health_bar_height)
        .attr("class", 'lifebar')

        var mbar = svg.append("rect")
        .attr("x", 0)
        .attr("y", health_bar_height)
        .attr("width", width)
        .attr("height", health_bar_height)
        .attr("class", val['name']+' mana-bar');

        var hbar = svg.append("rect")
        .attr("x", 0)
        .attr("y", 0)
        .attr("width", width)
        .attr("height", health_bar_height)
        .attr("class", val['name']+' health-bar');

        // Listen for the update
        $(document).on('update', function(e, snapshot){
            var health_width = width*snapshot[idx]['health']/snapshot[idx]['max_health']
            hbar.transition()
                .duration(params.interval_duration)
                .attr('width', health_width)
            if(health_width === 0){}
            mbar.attr(
                'width',
                width*snapshot[idx]['mana']/snapshot[idx]['max_mana']
            )
        })

    })

}
window.healthBars = healthBars
