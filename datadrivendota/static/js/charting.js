"use strict";

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
        .replace(/ /g,"-")
        .replace(/[^\w-]+/g,"")
        ;
}

function toTitleCase(str)
{
    return str.replace(/\w\S*/g, function(txt){
      return txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase();
    }).replace(/\_/g, " ");
}

var getVals = function(obj){
   var vals = [];
   for(var key in obj){
      vals.push(obj[key]);
   }
   return vals;
}

function getColorScale(params){
  if ("color_range" in params && "color_domain" in params) {
      var color = d3.scale.ordinal()
              .range(params.color_range)
              .domain(params.color_domain);
  }
  else {
      var color = d3.scale.category10();
  }

  return color;
}

window.Chartreuse = {};

function make_svg(destination, width, height){
  if (width === undefined){
    width = $(destination).width();
  }
  if (height === undefined){
    height = width;
  }
  return d3.select(destination)
    .append("svg")
    .attr("width", width)
    .attr("height", width);
}

window.Chartreuse.make_svg = make_svg;

var winrate_scatter = function(winrate_data, dossier_data, destination){

  var chart;
  var chart_data;

  nv.addGraph(
    function(){
      chart = nv.models.scatterChart()
        .margin({
          left: 45,
          bottom: 45,
        })
        .forceY([0,100])
        .showLegend(false);
      chart.tooltip.enabled();

      var plot_data = [
        {
          key: "Winrate",
          values: winrate_data.map(function(v){
            var datum = {
              y: v.games ? +(v.wins/v.games * 100).toFixed(2) : 0,
              x: v.games ? v.games : 0,
              hero: v.hero,
            };
            return datum;
          })
        }
      ];
      console.log(plot_data);
      chart.xAxis.axisLabel("# Games");
      chart.yAxis.axisLabel("Win %").axisLabelDistance(-20);

      var svg = make_svg(destination);
      chart_data = svg.datum(plot_data);
      chart_data.transition().duration(500).call(chart);


      return chart;
    },
    function(chart){
      var place = destination + ' path.nv-point';

      d3.selectAll(place).attr(
        'class',
        function(d){
            var hero_name = (d[0].hero || {}).internal_name || '';
            var hero = dossier_data.filter(function(d){
              return d.hero.internal_name === hero_name
            })[0]
            return d3.select(this).attr('class') + ' '+ hero.alignment + ' ' + hero_name;
        }
      );
    }
  );

  return chart;
};

window.Chartreuse.winrate_scatter = winrate_scatter;


var pickban_scatter_walk = function(plot_data, destination, cb){

  var chart;
  var chart_data;
  var svg = make_svg(destination);

  nv.addGraph(
    function(){
      chart = nv.models.scatterChart()
        .margin({
          left: 45,
          bottom: 45,
        })
        .x(function(d){return d.bans;})
        .y(function(d){return d.picks;})
        .useVoronoi(false)
        .showLegend(false);
      chart.tooltip.enabled();

      chart.xAxis.axisLabel("# Games Banned");
      chart.yAxis.axisLabel("# Games Picked").axisLabelDistance(-20);

      chart_data = svg.datum(plot_data);
      chart_data.transition().duration(500).call(chart);
      console.log('Drew');
      return chart;
    },
    function(chart){
      var place = destination + ' path.nv-point';

      d3.selectAll(place).attr(
        'class',
        function(d){
            var hero_name = (d[0].hero || {}).internal_name || '';
            var hero = d[0].hero;
            return d3.select(this).attr('class') + ' '+ hero.alignment + ' ' + hero_name;
        }
      );
      cb(svg, chart);
    }
  );

};

window.Chartreuse.pickban_scatter_walk = pickban_scatter_walk;

var pickban_scatter = function(data, destination){

  var chart;
  var chart_data;

  nv.addGraph(function(){
    var plot_data = [
      {
        key: "Picks & Bans",
        values: data.map(function(v){
          var datum = {
            x: +v.picks.toFixed(0),
            y: +v.bans.toFixed(0),
            hero: v.hero,
          };
          return datum;
        })
      }
    ]

    chart = nv.models.scatterChart()
      .margin({
        left: 45,
        bottom: 45,
      })
      .showLegend(false);
    chart.tooltip.enabled();

    chart.xAxis.axisLabel("Picks");
    chart.yAxis.axisLabel("Bans").axisLabelDistance(-20);


    var svg = make_svg(destination);
    chart_data = svg.datum(plot_data);
    chart_data.transition().duration(500).call(chart);

    return chart;
  });

  return chart;
};

window.Chartreuse.pickban_scatter = pickban_scatter;

var scatter = function(destination, plot_data, xlab, ylab){
  nv.addGraph(function(){

    var svg = window.make_svg(destination, 230);

    var chart = nv.models.scatterChart().showLegend(false)
      .margin({
        left:60,
        bottom:40
      });

    chart.xAxis.axisLabel(xlab).axisLabelDistance(-10);
    chart.yAxis.axisLabel(ylab).axisLabelDistance(-10);
    chart.xAxis.tickFormat(window.smartTicks);
    chart.yAxis.tickFormat(window.smartTicks);

    var chart_data = svg.datum(plot_data);
    chart_data.transition().duration(500).call(chart);

  });
};

window.Chartreuse.scatter = scatter;

var splash_gimmick = function(){
  var mydiv = d3.select('div.big-d');
  var width = 220;
  var height = width;
  var delay = 1000;
  var interval = 1500;

  var r = 5;
  var point_max = 75;

  var x_min = 0;
  var x_max = 10;

  var y_min = 0;
  var y_max = 10;

  var x_domain = [-5, 9];
  var y_domain = [-1, 12];

  var svg = mydiv.append('svg')
      .attr('width', width)
      .attr('height', height);

  var x_scale = d3.scale
      .linear()
      .domain(x_domain)
      .range([0, width])

  var y_scale = d3.scale
      .linear()
      .domain(y_domain)
      .range([height, 0])

  var datapoints = [];
  var intersection_x = 6;
  var lines = [
      {
        m: 99999999,
        b: 0,
        class_odds: [.1, .4, .5],
        x_domain: [0, 1],
        y_domain: [0, 10]
      },
      {
        m: -5/intersection_x,
        b: 10,
        class_odds: [.1, .6, .3],
        x_domain: [0, intersection_x],
        y_domain: [-.5, .5]
      },
      {
        m: 5/intersection_x,
        b: 0,
        class_odds: [.7, .1, .2],
        x_domain: [0, intersection_x],
        y_domain: [-.5, .5]
      },
  ];

  var n = 0
  var make_point = function(line){
    n += 1;
    if (n>point_max*2){
      n-=point_max*2;
    }

    // x_rand = z.nextGaussian();
    // y_rand = z.nextGaussian();
    x_rand = Math.random();
    var x = x_rand*(line.x_domain[1]-line.x_domain[0])-line.x_domain[0];

    if(line.m < 99999999){
      y_rand = Math.random();
      var y = (x*line.m+line.b)+y_rand;
    }
    else {
      y_rand = Math.random();
      var y = y_rand*(line.y_domain[1]-line.y_domain[0])-line.y_domain[0];
    }

    class_str = classify(line)
    return {
        'x': x,
        'y': y,
        'x_rand': x_rand,
        'y_rand': y_rand,
        'classing': class_str,
        'id': n,
    }
  }

  var classify = function(line){
    class_rand = Math.random();
    var break_1 = line.class_odds[0];
    var break_2 = break_1 + line.class_odds[1];
    var break_3 = break_2 + line.class_odds[2];

    if(class_rand < break_1){
      return 'group-a'
    }
    else if(class_rand < break_2){
      return 'group-b'
    }
    else {
      return 'group-c'
    }

  }

  var update = function(){

      for(var i=0; i<lines.length; i++){

          datapoints.push(
              make_point(lines[i])
          )
          datapoints.push(
              make_point(lines[i])
          )
          datapoints.push(
              make_point(lines[i])
          )
          datapoints.push(
              make_point(lines[i])
          )

          while(datapoints.length>point_max){
              datapoints.shift();
          }
      }

      circles = svg.selectAll('circle')
          .data(datapoints, function(d){
              return d.id;
          })

      circles
          .enter()
          .append('circle')
          .attr('cx', function(d){
              return x_scale(d.x);
          })
          .attr('cy', function(d){
              return y_scale(d.y);
          })
          .attr('r', 0)
          .attr('class', function(d){return d.classing})
          .transition()
          .delay(delay)
          .attr('r', r)

      circles
        .exit()
        .transition()
        .delay(delay)
        .attr('r', 0)
        .remove();

    // Fix Averages in table
    var round_places = 2;
    groups = ['group-a', 'group-b', 'group-c',]
    for(var i=0; i < groups.length; i++){

      var selection = datapoints.filter(function(d){
        return d.classing == groups[i]
      })

      var x_mean = d3.mean(selection, function(d){return d.x}).toFixed(round_places);
      selector_class = '#'+groups[i]+'-x';
      $(selector_class).html(x_mean);

      var y_mean = d3.mean(selection, function(d){return d.y}).toFixed(round_places);
      selector_class = '#'+groups[i]+'-y';
      $(selector_class).html(y_mean);

    }

  }

  setInterval(update, interval);
}
window.splash_gimmick = splash_gimmick;


var cumsum_heroes = function(data, attr){
  for (var j=0; j < data.length; j++){
      for(var i=0; i < data[j]['values'].length; i++){
          if (i==0) {}
          else {
              data[j]['values'][i].value += data[j]['values'][i-1].value;
          }
      }
  }
  return data;
}
