"use strict"
var d3 = window.d3;


var heroContentGenerator = function(getX, getY, xlab, ylab){
  var return_fn = function(d){
      if (d === null) {return "";}
      d = d[0];
      var table = d3.select(document.createElement("table"));

      // Make a header
      var theadEnter = table
          .selectAll("thead")
          .data([d])
          .enter()
          .append("thead");

      var trowEnter = theadEnter
          .append("tr");

      trowEnter.append("td")
      .html(function(p){
        return p.hero.name;
      });

      trowEnter
        .append("td")
        .append("i")
        .attr(
          "class",
          function(p){return "d2mh " + p.hero.internal_name;}
        );

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html(xlab+": ");

      trowEnter2.append("td")
          .classed("value", true)
          .html(function(p) {return getX(p);});


      var tBodyRowEnter = tbodyEnter.append("tr");

      tBodyRowEnter
          .append("td")
          .html(ylab+": ");

      tBodyRowEnter.append("td")
          .classed("value",true)
          .html(
            function(p, i) {
                return getY(p);
            }
          );

      tBodyRowEnter.selectAll("td").each(function(p) {
          if (p.highlight) {
              var opacityScale = d3.scale.linear()
              .domain([0,1])
              .range(["#fff", p.color]);

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

  };
  return return_fn;
};

var bldg_tooltip = function(d, x, y, z){
      if (d === null) {return "";}
      d = d.point;
      var table = d3.select(document.createElement("table"));

      var clean = function(str){
        if (str.slice(0,12)=="npc_dota_bad") {
            return str.replace("\_"," ").slice(17,99);
        } else {
            return str.replace("\_"," ").slice(18,99);
        }
      }

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter1 = tbodyEnter
          .append("tr");

      trowEnter1
          .append("td")
          .html("Bldg: ");

      trowEnter1.append("td")
          .classed("value", true)
          .html(function(x){
            return clean(x.key);
        });

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html("Time: ");

      trowEnter2.append("td")
          .classed("value", true)
          .html(function(x){return String(x.offset_time).toHHMMSS()});

      var trowEnter3 = tbodyEnter
          .append("tr");

      trowEnter3
          .append("td")
          .html("Killer: ");

      trowEnter3.append("td")
          .classed("value", true)
          .html(function(x){return x.unit.replace('npc_dota_hero_','').replace("_"," ");});


      var html = table.node().outerHTML;
      return html;

};

var item_tooltip = function(d, x, y, z){
      if (d === null) {return "";}
      d = d.point;
      var table = d3.select(document.createElement("table"));

      // Make a body
      var tbodyEnter = table
          .selectAll("tbody")
          .data([d])
          .enter()
          .append("tbody");

      var trowEnter1 = tbodyEnter
          .append("tr");

      trowEnter1
          .append("td")
          .html("Item: ");

      trowEnter1.append("td")
          .classed("value", true)
          .html(function(x){
            return x.key;
        });

      var trowEnter2 = tbodyEnter
          .append("tr");

      trowEnter2
          .append("td")
          .html("Time: ");

      trowEnter2.append("td")
          .classed("value", true)
          .html(function(x){return String(x.offset_time).toHHMMSS()});

      var trowEnter3 = tbodyEnter
          .append("tr");

      trowEnter3
          .append("td")
          .html("Hero: ");

      trowEnter3.append("td")
          .classed("value", true)
          .html(function(x){
            return x.unit.replace('npc_dota_hero_','').replace("_"," ");
          });


      var html = table.node().outerHTML;
      return html;

};

module.exports = {
    hero_tooltip: heroContentGenerator,
    bldg_tooltip: bldg_tooltip,
    item_tooltip: item_tooltip,
};
