nv.extensions.models.classDiscreteBarChart = function(destination, plot_data){

    var svg = window.make_svg(destination);

    var chart = nv.models.discreteBarChart();

    chart.x(function(d){return d.label;})
          .y(function(d){return d.value;})
          .margin({
            bottom:120
          });

    svg.datum(plot_data)
      .transition()
      .duration(500)
      .call(chart);

    d3.select(destination + " .nv-x.nv-axis > g")
      .selectAll("g")
      .selectAll("text")
      .attr("transform", function(d,i,j) { return "translate (-7, 65) rotate(-90 0,0)"; }) ;

    return chart;

};
