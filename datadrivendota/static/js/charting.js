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

function make_svg(destination){
  return d3.select(destination)
    .append("svg")
    .attr("width", $(destination).width())
    .attr("height", $(destination).width());
}

window.Chartreuse = {};

var winrate_scatter = function(data, destination){

  var chart;
  var chart_data;

  nv.addGraph(function(){
    chart = nv.models.scatterChart()
      .tooltips(true)
      .margin({
        left: 30,
        bottom: 30,
      })
      .forceY([0,100])
      .showLegend(false)
      .tooltipContent(function(key, x, y, _, datum) {
        return "<h3>" + key + "</h3>" + "<p>"+datum.point.hero.name+"</p>";
      });

    var plot_data = [
      {
        key: "Winrate",
        values: data.map(function(v){
          var datum = {
            y: v.games ? +(v.wins/v.games * 100).toFixed(2) : 0,
            x: v.games ? v.games : 0,
            hero: v.hero,
          };
          return datum;
        })
      }
    ]

    var svg = make_svg(destination);
    chart_data = svg.datum(plot_data);
    chart_data.transition().duration(500).call(chart);

    return chart;
  });

  return chart;
};

window.Chartreuse.winrate_scatter = winrate_scatter;



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
      .tooltips(true)
      .margin({
        left: 30,
        bottom: 30,
      })
      .showLegend(false)
      .tooltipContent(function(key, x, y, _, datum) {
        return "<h3>" + key + "</h3>" + "<p>"+datum.point.hero.name+"</p>";
      });


    var svg = make_svg(destination);
    chart_data = svg.datum(plot_data);
    chart_data.transition().duration(500).call(chart);

    return chart;
  });

  return chart;
};

window.Chartreuse.pickban_scatter = pickban_scatter;
