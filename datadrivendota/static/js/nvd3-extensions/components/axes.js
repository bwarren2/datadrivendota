var offset_time = {
    label: "Minutes from Horn",
    access: function(d){
        return d.offset_time;
    }
};

var sum = {
  label: "Total",
  access: function(d){return d.sum;}
};

module.exports = {
    sum: sum,
    offset_time: offset_time,
}
