'use strict';

var $ = window.$;

var toggle_sides = function(){

        var idx = 0;
        setInterval(function(){

          if(idx===0){
            $(' div.toggling g.nv-series-0, div.toggling g.nv-series-1, div.toggling g.nv-series-2, div.toggling g.nv-series-3, div.toggling g.nv-series-4').fadeIn();

            $(' div.toggling g.nv-series-5, div.toggling g.nv-series-6, div.toggling g.nv-series-7, div.toggling g.nv-series-8, div.toggling g.nv-series-9').fadeIn();

          }else if(idx==1){
            $(' div.toggling g.nv-series-0, div.toggling g.nv-series-1, div.toggling g.nv-series-2, div.toggling g.nv-series-3, div.toggling g.nv-series-4').fadeOut();

            $(' div.toggling g.nv-series-5, div.toggling g.nv-series-6, div.toggling g.nv-series-7, div.toggling g.nv-series-8, div.toggling g.nv-series-9').fadeIn();

          }else if(idx==2){
            $(' div.toggling g.nv-series-0, div.toggling g.nv-series-1, div.toggling g.nv-series-2, div.toggling g.nv-series-3, div.toggling g.nv-series-4').fadeIn();

            $(' div.toggling g.nv-series-5, div.toggling g.nv-series-6, div.toggling g.nv-series-7, div.toggling g.nv-series-8, div.toggling g.nv-series-9').fadeOut();

          }
          idx = (idx + 1)%3;
        }, 3000);
}

module.exports = {
    toggle_sides: toggle_sides
}
