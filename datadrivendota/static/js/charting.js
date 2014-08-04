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
