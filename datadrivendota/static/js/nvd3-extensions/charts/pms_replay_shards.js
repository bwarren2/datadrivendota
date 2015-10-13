"use strict";
var utils = require("../utils");
var Promise = require("bluebird");
var AjaxCache = require("../ajax_cache");
var models = require("../models");
var $ = window.$;
var nv = window.nv;
var d3 = window.d3;
var tooltips = require("./tooltips.js");

var shard_lineup = function(destination, params){
  Promise.join(
    AjaxCache.get({
        url: "https://s3.amazonaws.com/datadrivendota/media/playermatchsummaries/replays/1837060998_1_parse_shard.json.gz",
        dataType: "json",
    }),
    AjaxCache.get({
        url: "https://s3.amazonaws.com/datadrivendota/media/playermatchsummaries/replays/1837060998_130_parse_shard.json.gz",
        dataType: "json",
    })

  ).then(function(data){
    $(destination).empty();
    var plot_data = data.map(function(d){
      var cumsum = 0;
      return {
        "key": toTitleCase(d[0].unit),
        "values": d.filter(function(m){
          return m.type == "gold_reasons";
        }).map(function(m){
          m.cumsum = cumsum + m.value;
          cumsum += m.value;
          return m;
        })
      };
    });
    var chart;
    var chart_data;
    var svg = utils.svg.square_svg(destination);

    var xlab = "Time";
    var ylab = "Gold";

    nv.addGraph(

      function(){
        chart = nv.models.lineChart()
          .margin({
            left: 45,
            bottom: 45,
          })
          .x(function(d){return d.offset_time;})
          .y(function(d){return d.cumsum;})
          .showLegend(false)
          .interpolate('step-after');

        chart.xAxis.axisLabel(xlab);
        chart.yAxis.axisLabel(ylab).axisLabelDistance(-20);

        chart_data = svg.datum(plot_data);
        chart_data.transition().duration(500).call(chart);
        return chart;
      }
    );

  }).catch(function(e){
    console.log(e);
  });
};

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
};


var contentGenerator = function(getX, getY, xlab, ylab){
  var return_fn = function(d){
      if (d === null) {
        return '';
      }
      getx = getX;
      gety = getY;
      var table = d3.select(document.createElement("table"));


        var theadEnter = table.selectAll("thead")
            .data([d])
            .enter().append("thead");

        var trowEnter = theadEnter.selectAll("tr")
                .data(function(p) { return p.series})
                .enter()
                .append("tr")
                .classed("highlight", function(p) { return p.highlight});

        trowEnter.append("td")
            .classed("legend-color-guide",true)
            .append("div")
            .style("background-color", function(p) { return p.color});

        trowEnter.append("td")
            .classed("key", true)
            .classed("total",function(p) { return !!p.total})
            .html(function(p) { return p.key});
      // if (headerEnabled) {}

      var tbodyEnter = table.selectAll("tbody")
          .data([d])
          .enter().append("tbody");

      var trowEnter = tbodyEnter.append("tr");

      trowEnter
          .append("td")
          .html(xlab+': ');

      trowEnter.append("td")
          .classed("value",true)
          .html(function(p) {
            return getx(p)
        });


      var tBodyRowEnter = tbodyEnter.append("tr");

      tBodyRowEnter
          .append("td")
          .html(ylab+': ');

      tBodyRowEnter.append("td")
          .classed("value",true)
          .html(function(p, i) {
            return gety(p)
          });

      tBodyRowEnter.selectAll("td").each(function(p) {
          if (p.highlight) {
              var opacityScale = d3.scale.linear().domain([0,1]).range(["#fff",p.color]);
              var opacity = 0.6;
              d3.select(this)
                  .style("border-bottom-color", opacityScale(opacity))
                  .style("border-top-color", opacityScale(opacity))
              ;
          }
      });

      var html = table.node().outerHTML;
      if (d.footer !== undefined)
          html += "<div class='footer'>" + d.footer + "</div>";
      return html;

  }
  return return_fn
};


var hack = function(datatype, destination, xlab, ylab){
    $(destination).empty();

    Promise.resolve(
        AjaxCache.get({
            url: 'https://s3.amazonaws.com/datadrivendota/raw_replay_parse/1843672837_raw_parse.json',
            dataType: 'json'
        })
    ).then(function(replay){

      var gold = replay.filter(function(x){
          return x.type == datatype &&
          'npc_dota_hero_'==x.unit.slice(0, 14) &&
          (x.unit.slice(14,30) == 'nevermore' || x.unit.slice(14,30) == 'templar_assassin' );
      }).sort(function(a, b){
          return a.time > b.time;
      });

      var plot_data = d3.nest()
          .key(function(d){
            return toTitleCase(d.unit.slice(14).replace('_',' '))
          }).entries(gold);

      plot_data = cumsum_heroes(plot_data, 'value')

      nv.addGraph(function(){

          var svg = d3.select(destination)
            .append("svg")
            .attr("width", 900)
            .attr("height", 450);

          var chart = nv.models.lineChart()
              .x(function(d) {
                  return d.time;
              })
              .y(function(d) { return d.value })
              .color(d3.scale.category10().range())
              .showLegend(false)
              .interpolate('step-after');

          var accessx = function(a){return a.point.time};

          chart.xAxis.axisLabel(xlab).axisLabelDistance(-10);
          chart.yAxis.axisLabel(ylab).axisLabelDistance(-10);

          var chart_data = svg.datum(plot_data);
          chart_data.transition().duration(500).call(chart);

      })

    }).catch(function(jqXhr, err, errStr){})
};

module.exports = {
  shard_lineup: shard_lineup,
  hack: hack,
};
