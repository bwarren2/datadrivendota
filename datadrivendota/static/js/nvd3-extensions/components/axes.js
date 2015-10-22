var offset_time = {
    label: "Minutes from Horn",
    access: function(d){
        return d.offset_time;
    }
};

var cumsum = {
  label: "Total",
  access: function(d){return d.cumsum;}
};

module.exports = {
    cumsum: cumsum,
    offset_time: offset_time,
}
