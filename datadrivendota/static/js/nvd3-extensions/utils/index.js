'use strict';

var svg = require('./svg.js');
var blanks = require('./blanks.js');
var reduce = require('./reduce.js');

var getSet = function(value){
    var val = value;
    return {
        get: function(){
            return val;
        },
        set: function(_){
            val=_;
        }
    }
};

var getSetFunctor = function(value){
    var val = value;
    return {
        get: function(){
            return val;
        },
        set: function(_){
            val=d3.functor(_);

        }
    }
};

/*
Add a particular option from an options object onto chart
Options exposed on a chart are a getter/setter function that returns chart
on set to mimic typical d3 option chaining, e.g. svg.option1('a').option2('b');
option objects should be generated via Object.create() to provide
the option of manipulating data via get/set functions.
*/
var initOption = function(chart, name) {
    // if it's a call option, just call it directly, otherwise do get/set
    if (chart._calls && chart._calls[name]) {
        chart[name] = chart._calls[name];
    } else {
        chart[name] = function (_) {

            if (!arguments.length) return chart._options[name];
            chart._overrides[name] = true;
            chart._options[name] = _;
            return chart;
        };
        // calling the option as _option will ignore if set by option already
        // so nvd3 can set options internally but then stop if set manually
        chart['_' + name] = function(_) {
            if (!arguments.length) return chart._options[name];
            if (!chart._overrides[name]) {
                chart._options[name] = _;
            }
            return chart;
        }
    }
};


/*
Add all options in an options object to the chart
*/
var initOptions = function(chart) {
    chart._overrides = chart._overrides || {};
    var ops = Object.getOwnPropertyNames(chart._options || {});
    var calls = Object.getOwnPropertyNames(chart._calls || {});
    ops = ops.concat(calls);
    for (var i in ops) {
        initOption(chart, ops[i]);
    }
};

module.exports = {
    svg: svg,
    blanks: blanks,
    reduce: reduce,
    getSet: getSet,
    getSetFunctor: getSetFunctor,
    initOptions: initOptions,
}
