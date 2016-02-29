
var pretty_numbers = function(d){
    if(Math.abs(d)>1000000){return (d/1000000).toFixed(0) + "M";}
    else if(Math.abs(d)>1000){return (d/1000).toFixed(0) + "K";}
    else { return d; }
}
var pretty_times = function(d){
    return String(d).toHHMMSS();
}



module.exports = {
    pretty_numbers: pretty_numbers,
    pretty_times: pretty_times,
}
