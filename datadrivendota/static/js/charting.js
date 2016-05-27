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

function convertToSlug(text)
{
    return text
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
