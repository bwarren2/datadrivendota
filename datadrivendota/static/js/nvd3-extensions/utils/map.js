var count = function(icon){
    var icon = icon;

    return function(msg, idx, ary){
      var prev_index = idx-1;
      if (prev_index >= 0 && prev_index < ary.length){
        var prev_value = ary[prev_index].cumsum;
        msg.cumsum = prev_value + 1;
      } else{
        msg.cumsum = 1;
      }
      return msg;
    }
}


module.exports = {
    count: count
}
