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
              .domain(params.color_domain)
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
    return div
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
  inner.attr("width", width)
        .attr("height", height)
        .attr("class", 'inner-chart')
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

function draw_title(params, svg){
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
        return toTitleCase(d.key);
      });

}

function draw_legend(params, svg, color){
  var outerWidth = get_outer_width(params);
  var outerHeight = get_outer_height(params);
  var margin = get_margin(params);
  var legend = svg.append("g");
  var pctWidth = get_legend_width_pct(params)
  var pctHeight = get_legend_height_pct(params)
  legend.attr("class", "legend")
        .attr("transform", "translate("
          +outerWidth*pctWidth+
          ","
          +outerHeight/10+")");

  var rows = legend.selectAll('rect')
        .data(function(d){return d.values;})
        .enter();
      rows.append("rect")
        .attr("x", 2)
        .attr("y", function(d, i){ return i *  20;})
        .attr("width", 10)
        .attr("height", 10)
        .style("fill", function(d) {
           var return_color = color(d['key']);
           return return_color;
        })
        .on("mouseover",
          function (d, i) {
            slug = convertToSlug(d.key)
            d3.selectAll('g.series:not(.'+slug+')')
            .transition().duration(1000).style('opacity',0.2);
        })
        .on("mouseout", function(d) {
            slug = convertToSlug(d.key)
            d3.selectAll('g.series:not(.'+slug+')')
            .transition().duration(1000).style('opacity',1);
          }
        );

  rows.append('text')
    .attr("class", 'legend-text')
    .attr("x", 14)
    .attr("y", function(d, i){ return 11+(i *  20);})
    .text(function(d){
      return d.key;
    });
}

function draw_path(series, line, color){
    series.append("svg:path")
    .attr("d", function(d){return(line(d.values));})
    .style("stroke", function(d) {
      return color(String(d.values[0].group_var));
    })
    .style("stroke-width", 1)
    .style("fill", 'none');
}



function get_margin(params){
  return params.margin;
}

function get_padding(params){
  return params.padding;
}

function get_width(params){
  var padding = get_padding(params)
  return get_inner_width(params) - padding.left - padding.right;
}
function get_height(params){
  var padding = get_padding(params)
  return get_inner_height(params) - padding.top - padding.bottom;
}
function get_inner_width(params){
  var margin = get_margin(params)
  return get_outer_width(params) - margin.left - margin.right;
}
function get_inner_height(params){
  var margin = get_margin(params)
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

function draw_scatterplot(source, placement_div){
    var raw_data = source['data'];
    var params = source['parameters'];

    data = d3.nest().key(function(d){return d.split_var;}).key(function(d){return d.group_var;}).entries(raw_data);

    var div = make_tooltip()

    var svg = outer_chart(params, placement_div, data);

    var line = d3.svg.line()
        .interpolate("linear")
        .x(function(d) { return x(d.x_var); })
        .y(function(d) { return y(d.y_var); });

    var x = linear_x_scale(params);
    var y = linear_y_scale(params);

    var xAxis = d3.svg.axis().scale(x).orient("bottom"),
        yAxis = d3.svg.axis().scale(y).orient("left");

    var color = getColorScale(params)

    var g = inner_chart(params, svg);

    draw_x_axis(params, g, xAxis);
    draw_y_axis(params, g, yAxis);
    draw_title(params, svg)


    var series = g.selectAll('.series').data(function(d){
            return(d.values);
        }).enter().append('g')
    .attr("class", function(d){
      return 'series '+convertToSlug(d.values[0].group_var);
    })
    .attr("id", function(d){return convertToSlug(d.key);});

    series.selectAll('.points').data(function(d){return d.values;}).enter()
        .append("a").attr("xlink:href", function(d) {if(d.url){return d.url;} else {return '';}})
    .append('circle')
    .attr('cx',function(d){return(x(d.x_var)); })
    .attr('cy',function(d){return(y(d.y_var)); })
    .attr("class", 'points')
    .attr('r', 5)
    .style("fill", function(d) { return color(String(d.group_var));})
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
      series.append("svg:path")
      .attr("d", function(d){return(line(d.values));})
      .attr("class", 'datapath')

      .style("stroke", function(d) { return color(String(d.values[0].group_var));})
      .style("stroke-width", 3)
      .style("fill", 'none');
    }

    if(params['draw_legend']){
      draw_legend(params, svg, color)
    }
}
function draw_barplot(source, placement_div){
    var raw_data = source['data'];
    var params = source['parameters'];


    var width = get_width(params),
        height = get_height(params);

    data = d3.nest().key(function(d){return d.split_var;}).key(function(d){return d.group_var;}).entries(raw_data);

    var div = make_tooltip()
    var svg = outer_chart(params, placement_div, data);

    var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.1).domain(params.x_set);
    var y = linear_y_scale(params);

    var xAxis = d3.svg.axis().scale(x).orient("bottom").tickValues(params.tickValues),
        yAxis = d3.svg.axis().scale(y).orient("left");

    var color = getColorScale(params)
    var g = inner_chart(params, svg);

    draw_title(params, svg)

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


    var series = g.selectAll('.series').data(function(d){
            return(d.values);
        })
    .enter()
    .append('g')
    .attr("class", function(d) {
      return 'series '+convertToSlug(d.values[0].group_var);
    })
    .attr("id", function(d){return convertToSlug(d.key);});

    series.selectAll('.bars')
        .data(function(d){return d.values;}).enter()
        .append("a")
        .attr("xlink:href", function(d) {
          if(d.url){return d.url;}
          else {return '';}
        })
    .append('rect')
    .attr("x", function(d) { return x(d.x_var); })
    .attr("width", x.rangeBand())
    .attr("y", function(d) { return y(d.y_var); })
    .attr("height", function(d) { return height - y(d.y_var); })
    .style("fill", function(d) { return color(String(d.group_var));})
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
      series.append("svg:path").attr("d", function(d){return(line(d.values));})
      .style("stroke", function(d) { return color(d.values[0].group_var);})
      .style("stroke-width", 3)
      .style("fill", 'none');
    }

    if(params['draw_legend']){
      draw_legend(params, svg, color);
    }
}


function draw_scatterseries(data, placement_div){

  var raw_data = data['data'];
  var params = data['parameters'];
      params['draw_path'] = 'True'
      params['draw_legend'] = 'True'

  data = d3.nest().key(function(d){return d.split_var;}).key(function(d){return d.group_var;}).key(function(d){return d.series_var;}).entries(raw_data);

  var div = make_tooltip()

  var svg = outer_chart(params, placement_div, data);

  var line = d3.svg.line()
      .interpolate("linear")
      .x(function(d) { return x(d.x_var); })
      .y(function(d) { return y(d.y_var); });


  var x = linear_x_scale(params);
  var y = linear_y_scale(params);

  var xAxis = d3.svg.axis().scale(x).orient("bottom"),
      yAxis = d3.svg.axis().scale(y).orient("left");

  var color = getColorScale(params)

  var g = inner_chart(params, svg);

  draw_x_axis(params, g, xAxis);
  draw_y_axis(params, g, yAxis);

  draw_title(params, svg)

  var groups = g.selectAll('.groups').data(function(d){
          return(d.values);
      }).enter().append('g')
  .attr("class", 'group')
  .attr("id", function(d){return convertToSlug(d.key);});

  var series = groups.selectAll('.series').data(function(d){
              return d.values;
              })
              .enter()
              .append("g")
              .attr("class", function(d){
                return 'series '+convertToSlug(d.values[0].group_var);
              })
              .attr("id", function(d){return convertToSlug(d.key);});

  series.selectAll('.points').data(function(d){
        return d.values;}
      ).enter()
      .append('a')
      .attr("xlink:href", function(d) {
        if(d.url){return d.url;} else {return '';}
      })
      .append('circle')
      .attr('cx',function(d){return(x(d.x_var)); })
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
    draw_path(series, line, color);
  }

  if(params['draw_legend']){
    draw_legend(params, svg, color)
  }
}


function plot(source, div){
    if(source.parameters['chart']=='xyplot'){
        draw_scatterplot(source, div);
    }
    else if(source.parameters['chart']=='barplot'){
        draw_barplot(source, div);
    }
    else if(source.parameters['chart']=='scatterseries'){
        draw_scatterseries(source, div);
    }
}
window.d3ening = {}
window.d3ening.plot = plot
