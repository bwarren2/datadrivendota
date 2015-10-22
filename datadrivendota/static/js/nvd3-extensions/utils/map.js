'use strict';

var count = function(){
    return function(msg, idx, ary){
      var prev_index = idx-1;
      if (prev_index >= 0 && prev_index < ary.length){
        var prev_value = ary[prev_index].sum;
        msg.sum = prev_value + 1;
      } else{
        msg.sum = 1;
      }
      return msg;
    };
};

var sum = function(){

    return function(msg, idx, ary){

      var prev_index = idx-1;

      var adder;
      if (msg.hasOwnProperty('value')){
        adder = msg.value;
      } else{
        adder = 1;
      }
      if (prev_index >= 0 && prev_index < ary.length){
        var prev_value = ary[prev_index].sum;
        msg.sum = prev_value + adder;
      } else{
        msg.sum = adder;
      }
      return msg;
    };
};

module.exports = {
    count: count,
    sum: sum,
};
