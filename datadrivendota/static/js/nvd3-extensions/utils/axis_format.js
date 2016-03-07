
var pretty_numbers = function(d){
    if(Math.abs(d)>1000000){return (d/1000000).toFixed(0) + "M";}
    else if(Math.abs(d)>1000){return (d/1000).toFixed(0) + "K";}
    else { return d; }
}
var pretty_times = function(d){
    return String(d).toHHMMSS();
}

var minimap_x = function(width, height){
    return d3.scale.linear().domain([68,186]).range([
      .04*width, .96*width
    ]);
}

var minimap_y = function(width, height){
    return d3.scale.linear().domain([68,186]).range([
        .05*height, .96*height
    ]);
}



module.exports = {
    pretty_numbers: pretty_numbers,
    pretty_times: pretty_times,
    minimap_x: minimap_x,
    minimap_y: minimap_y,
}
