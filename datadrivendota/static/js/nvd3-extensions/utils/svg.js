function square_svg(destination, width, height){
  if (width === undefined){
    width = $(destination).width();
  }
  if (height === undefined){
    height = width;
  }
  return d3.select(destination)
    .append("svg")
    .attr("class", 'ddd-svg')
    .attr("width", width)
    .attr("height", width);
}

module.exports = {
  square_svg: square_svg,
}
