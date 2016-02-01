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

var match_tooltip = function(d, x, y, z){
      if (d === null) {return "";}
      d = d[0];

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
          .html("Match ID: ");

      trowEnter1.append("td")
          .html(function(x){
            return x.steam_id;
        });

      var trowEnter2 = tbodyEnter
          .append("tr");


      trowEnter2.append("td")
          .html('Teams');

      trowEnter2.append("td")
          .html(function(x){
            return x.radiant_team + ' vs. ' + x.dire_team
          });


      var html = table.node().outerHTML;
      return html;

};

var duel_tooltip_generator = function(x_name, y_name){

    var duel_tooltip = function(d, x, y, z){
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
              .html("Match Time: ");

          trowEnter1.append("td")
              .html(function(x){
                return String(x.offset_time).toHHMMSS();
            });

          var trowEnter2 = tbodyEnter
              .append("tr");

          trowEnter2.append("td")
              .html(x_name);

          trowEnter2.append("td")
              .html(function(x){
                return x.x
              });

          var trowEnter3 = tbodyEnter
              .append("tr");

          trowEnter3.append("td")
              .html(y_name);

          trowEnter3.append("td")
              .html(function(x){
                return x.y
              });


          var html = table.node().outerHTML;
          return html;

    };

return duel_tooltip;

};


var duel_item_tooltip_generator = function(x_name, y_name){

    var duel_tooltip = function(d, x, y, z){
          if (d === null) {return "";}
          d = d.point;

          var table = d3.select(document.createElement("table"));

          // Make a body
          var tbodyEnter = table
              .selectAll("tbody")
              .data([d])
              .enter()
              .append("tbody");

          var trowEnter0 = tbodyEnter
              .append("tr");

          trowEnter0
              .append("td")
              .html("Item: ");

          trowEnter0.append("td")
              .html(function(x){
                return toTitleCase(x.item.substring(5));
            });

          var trowEnter2 = tbodyEnter
              .append("tr");

          trowEnter2.append("td")
              .html(x_name);

          trowEnter2.append("td")
              .html(function(x){
                return String(x.x).toHHMMSS()
              });

          var trowEnter3 = tbodyEnter
              .append("tr");

          trowEnter3.append("td")
              .html(y_name);

          trowEnter3.append("td")
              .html(function(x){
                return String(x.y).toHHMMSS()
              });

          var trowEnter3 = tbodyEnter
              .append("tr");

          trowEnter3.append("td")
              .html('(Cost)');

          trowEnter3.append("td")
              .html(function(x){
                return String(x.cost)
              });


          var html = table.node().outerHTML;
          return html;

    };

return duel_tooltip;

};


module.exports = {
    hero_tooltip: heroContentGenerator,
    bldg_tooltip: bldg_tooltip,
    item_tooltip: item_tooltip,
    match_tooltip: match_tooltip,
    duel_tooltip_generator: duel_tooltip_generator,
    duel_item_tooltip_generator: duel_item_tooltip_generator,
};
