
var pretty_numbers = function(d){
    if(Math.abs(d)>1000000){return (d/1000000).toFixed(0) + "M";}
    else if(Math.abs(d)>1000){return (d/1000).toFixed(0) + "K";}
    else { return d; }
}
var pretty_times = function(d){
    return String(d).toHHMMSS();
}

var minimap_x = function(width, height){
    width = Math.min(width, height);
    return d3.scale.linear().domain([68,186]).range([
      .025*width, .973*width
    ]);
}

var minimap_y = function(width, height){
    height = Math.min(width, height);
    return d3.scale.linear().domain([68,186]).range([
        // .94*height, 0.03*height,
        .95*height, 0.03*height,
    ]);
}



module.exports = {
    pretty_numbers: pretty_numbers,
    pretty_times: pretty_times,
    minimap_x: minimap_x,
    minimap_y: minimap_y,
}
