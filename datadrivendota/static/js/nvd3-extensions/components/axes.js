var offset_time = {
  label: "Time",
  access: function(d){return d.offset_time;}
};
var cumsum = {
  label: "Time",
  access: function(d){return d.cumsum;}
};

module.exports = {
    cumsum: cumsum,
    offset_time: offset_time,
}
