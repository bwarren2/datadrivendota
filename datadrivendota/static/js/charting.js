function draw_scatterplot(source, placement_div){
    var raw_data = source['data'];
    var params = source['parameters'];


    var margin = params.margin,
        padding = params.padding,
        outerWidth = params.outerWidth,
        outerHeight = params.outerHeight,
        innerWidth = outerWidth - margin.left - margin.right,
        innerHeight = outerHeight - margin.top - margin.bottom,
        width = innerWidth - padding.left - padding.right,
        height = innerHeight - padding.top - padding.bottom;

    data = d3.nest().key(function(d){return d.split_var;}).key(function(d){return d.group_var;}).entries(raw_data);

    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);


    var svg = d3.select(placement_div).selectAll("svg")
        .data(data)
        .enter().append("svg:svg")
        .attr("width", outerWidth)
        .attr("height", outerHeight);

    var line = d3.svg.line()
        .interpolate("linear")
        .x(function(d) { return x(d.x_var); })
        .y(function(d) { return y(d.y_var); });


    var x = d3.scale.linear().domain([params['x_min'],params['x_max']]).range([0, width]);
        var y = d3.scale.linear().domain([params['y_min'], params['y_max']]).range([height,0]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom"),
        yAxis = d3.svg.axis().scale(y).orient("left");

    var color = d3.scale.category10();

    var g = svg.append("g")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    g.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis)
        .append("text")
          .attr("y", -16)
          .attr("x", width)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text(params['x_label']);

    g.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0,0)")
        .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text(params['y_label']);

    svg.append("g")
    .attr('class','title')
    .attr("transform", "translate(0,0)")
    .append("text")
      .attr("x", outerWidth/2)
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .text(function(d){return d.key;});

    var series = g.selectAll('.series').data(function(d){
            return(d.values);
        }).enter().append('g')
    .attr("class", 'dataset')
    .attr("id", function(d){return convertToSlug(d.key);});

    series.selectAll('.points').data(function(d){return d.values;}).enter()
        .append("a").attr("xlink:href", function(d) {if(d.url){return d.url;} else {return '';}})
    .append('circle')
    .attr('cx',function(d){return(x(d.x_var)); })
    .attr('cy',function(d){return(y(d.y_var)); })
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
      series.append("svg:path").attr("d", function(d){return(line(d.values));})
      .style("stroke", function(d) { return color(String(d.values[0].group_var));})
      .style("stroke-width", 3)
      .style("fill", 'none');
    }

    if(params['draw_legend']){
        var legend = g.append("g")
          .attr("class", "legend")
          .attr("height", 100)
          .attr("width", 100)
          .attr("transform", "translate("+width/10+","+height/10+")");

        var rows = legend.selectAll('rect')
              .data(function(d){return d.values;})
              .enter();
            rows.append("rect")
              .attr("x", 50)
              .attr("y", function(d, i){ return i *  20;})
              .attr("width", 10)
              .attr("height", 10)
              .style("fill", function(d) {
                 var return_color = color(d.values[0].group_var);
                 return return_color;
              })
              .on("mouseover",
                function (d, i) {
                  d3.selectAll('.dataset').filter(function(p){return convertToSlug(p.key)!=convertToSlug(d.key);})
                  .transition().duration(1000).style('opacity',0.2);
              })
              .on("mouseout", function(d) {
                    d3.selectAll('.dataset').filter(function(p){return convertToSlug(p.key)!=convertToSlug(d.key);})
                    .transition().duration(1000).style('opacity',1);
            });

            rows.append('text')
              .attr("x", 62)
              .attr("y", function(d, i){ return 11+(i *  20);})
              .text(function(d){return d.key;});
    }
}
function draw_barplot(source, placement_div){
    var raw_data = source['data'];
    var params = source['parameters'];


    var margin = params.margin,
        padding = params.padding,
        outerWidth = params.outerWidth,
        outerHeight = params.outerHeight,
        innerWidth = outerWidth - margin.left - margin.right,
        innerHeight = outerHeight - margin.top - margin.bottom,
        width = innerWidth - padding.left - padding.right,
        height = innerHeight - padding.top - padding.bottom;

    data = d3.nest().key(function(d){return d.split_var;}).key(function(d){return d.group_var;}).entries(raw_data);

    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);


    var svg = d3.select(placement_div).selectAll("svg")
        .data(data)
        .enter().append("svg:svg")
        .attr("width", outerWidth)
        .attr("height", outerHeight);

    var x = d3.scale.ordinal().rangeRoundBands([0, width], 0.1).domain(params.x_set);
    var y = d3.scale.linear().domain([params['y_min'], params['y_max']]).range([height,0]);

    var xAxis = d3.svg.axis().scale(x).orient("bottom").tickValues(params.tickValues),
        yAxis = d3.svg.axis().scale(y).orient("left");

    var color = d3.scale.category10();

    var g = svg.append("g")
        .attr("width", width)
        .attr("height", height)
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    g.append("g")
        .attr("class", "x axis")
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

    g.append("g")
        .attr("class", "y axis")
        .attr("transform", "translate(0,0)")
        .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text(params['y_label']);

    g.append("g")
    .attr('class','title')
    .attr("transform", "translate(0,0)")
    .append("text")
      .attr("x", width/2*1.2)
      .attr("dy", ".71em")
      .style("text-anchor", "end")
      .text(function(d){return d.key;});

    var series = g.selectAll('.series').data(function(d){
            return(d.values);
        }).enter().append('g')
    .attr("class", 'dataset')
    .attr("id", function(d){return convertToSlug(d.key);});

    series.selectAll('.bars').data(function(d){return d.values;}).enter()
        .append("a").attr("xlink:href", function(d) {if(d.url){return d.url;} else {return '';}})
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
        var legend = svg.append("g")
          .attr("class", "legend")
          .attr("height", 100)
          .attr("width", 100)
        .attr("transform", "translate(10,20)");

        var rows = legend.selectAll('rect')
              .data(function(d){return d.values;})
              .enter();
            rows.append("rect")
              .attr("x", 50)
              .attr("y", function(d, i){ return i *  20;})
              .attr("width", 10)
              .attr("height", 10)
              .style("fill", function(d) {
                 var return_color = color(d.values[0].group_var);
                 return return_color;
              })
              .on("mouseover",
                function (d, i) {
                  d3.selectAll('.dataset').filter(function(p){return convertToSlug(p.key)!=convertToSlug(d.key);})
                  .transition().duration(1000).style('opacity',0.2);
              })
              .on("mouseout", function(d) {
                    d3.selectAll('.dataset').filter(function(p){return convertToSlug(p.key)!=convertToSlug(d.key);})
                    .transition().duration(1000).style('opacity',1);
            });

            rows.append('text')
              .attr("x", 62)
              .attr("y", function(d, i){ return 11+(i *  20);})
              .text(function(d){return d.key;});
    }
}

function plot(source, div){
    if(source.parameters['chart']=='xyplot'){
        draw_scatterplot(source, div);
    }
    else if(source.parameters['chart']=='barplot'){
        draw_barplot(source, div);
    }
}
window.d3ening = {}
window.d3ening.plot = plot