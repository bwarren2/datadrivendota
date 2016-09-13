"use strict";
var models = require("./scatter.js");
var d3 = window.d3;
var nv = window.nv;
var mytip = require("./d3-tip.js")(d3);
var scatter_chart = function() {

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    var scatter      = models.scatter();
    var xAxis        = nv.models.axis();
    var yAxis        = nv.models.axis();
    var legend       = nv.models.legend();
    var distX        = nv.models.distribution();
    var distY        = nv.models.distribution();
    var contentGenerator      = function(d){return d;};

    var margin       = {top: 30, right: 20, bottom: 50, left: 75};
    var width        = null;
    var height       = null;
    var container    = null;
    var color        = nv.utils.defaultColor();
    var x            = scatter.xScale();
    var y            = scatter.yScale();
    var showDistX    = false;
    var showDistY    = false;
    var showLegend   = true;
    var showXAxis    = true;
    var showYAxis    = true;
    var rightAlignYAxis = false;
    var state = nv.utils.state();
    var defaultState = null;
    var dispatch = d3.dispatch("stateChange", "changeState", "renderEnd");
    var noData       = null;
    var duration = 250;

    scatter.xScale(x).yScale(y);
    xAxis.orient("bottom").tickPadding(10);
    yAxis
        .orient((rightAlignYAxis) ? "right" : "left")
        .tickPadding(10)
    ;
    distX.axis("x");
    distY.axis("y");

    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var x0;
    var y0;
    var renderWatch = nv.utils.renderWatch(dispatch, duration);

    var stateGetter = function(data) {
        return function(){
            return {
                active: data.map(function(d) { return !d.disabled; })
            };
        };
    };

    var stateSetter = function(data) {
        return function(state) {
            if (state.active !== undefined)
                data.forEach(function(series,i) {
                    series.disabled = !state.active[i];
                });
        };
    };

    function chart(selection) {
        renderWatch.reset();
        renderWatch.models(scatter);
        if (showXAxis) renderWatch.models(xAxis);
        if (showYAxis) renderWatch.models(yAxis);
        if (showDistX) renderWatch.models(distX);
        if (showDistY) renderWatch.models(distY);

        selection.each(function(data) {
            var that = this;

            container = d3.select(this);
            nv.utils.initSVG(container);

            var availableWidth = nv.utils.availableWidth(width, container, margin),
                availableHeight = nv.utils.availableHeight(height, container, margin);

            chart.update = function() {
                if (duration === 0)
                    container.call(chart);
                else
                    container.transition().duration(duration).call(chart);
            };
            chart.container = this;

            state
                .setter(stateSetter(data), chart.update)
                .getter(stateGetter(data))
                .update();

            // DEPRECATED set state.disableddisabled
            state.disabled = data.map(function(d) { return !!d.disabled; });

            if (!defaultState) {
                var key;
                defaultState = {};
                for (key in state) {
                    if (state[key] instanceof Array)
                        defaultState[key] = state[key].slice(0);
                    else
                        defaultState[key] = state[key];
                }
            }

            // Display noData message if there"s nothing to show.
            if (!data || !data.length || !data.filter(function(d) { return d.values.length; }).length) {
                nv.utils.noData(chart, container);
                renderWatch.renderEnd("scatter immediate");
                return chart;
            } else {
                container.selectAll(".nv-noData").remove();
            }

            // Setup Scales
            x = scatter.xScale();
            y = scatter.yScale();

            // Setup containers and skeleton of chart
            var wrap = container.selectAll("g.nv-wrap.nv-scatterChart").data([data]);
            var wrapEnter = wrap.enter().append("g").attr("class", "nvd3 nv-wrap nv-scatterChart nv-chart-" + scatter.id());
            var gEnter = wrapEnter.append("g");
            var g = wrap.select("g");

            // background for pointer events
            gEnter.append("rect").attr("class", "nvd3 nv-background").style("pointer-events","none");

            gEnter.append("g").attr("class", "nv-x nv-axis");
            gEnter.append("g").attr("class", "nv-y nv-axis");
            gEnter.append("g").attr("class", "nv-scatterWrap");
            gEnter.append("g").attr("class", "nv-regressionLinesWrap");
            gEnter.append("g").attr("class", "nv-distWrap");
            gEnter.append("g").attr("class", "nv-legendWrap");

            if (rightAlignYAxis) {
                g.select(".nv-y.nv-axis")
                    .attr("transform", "translate(" + availableWidth + ",0)");
            }

            // Legend
            if (showLegend) {
                var legendWidth = availableWidth;
                legend.width(legendWidth);

                wrap.select(".nv-legendWrap")
                    .datum(data)
                    .call(legend);

                if ( margin.top != legend.height()) {
                    margin.top = legend.height();
                    availableHeight = nv.utils.availableHeight(height, container, margin);
                }

                wrap.select(".nv-legendWrap")
                    .attr("transform", "translate(0" + "," + (-margin.top) +")");
            }

            wrap.attr("transform", "translate(" + margin.left + "," + margin.top + ")");

            // Main Chart Component(s)
            scatter
                .width(availableWidth)
                .height(availableHeight)
                .color(data.map(function(d,i) {
                    d.color = d.color || color(d, i);
                    return d.color;
                }).filter(function(d,i) { return !data[i].disabled; }));

            wrap.select(".nv-scatterWrap")
                .datum(data.filter(function(d) { return !d.disabled; }))
                .call(scatter);


            // Setup Axes
            if (showXAxis) {
                xAxis
                    .scale(x)
                    ._ticks( nv.utils.calcTicksX(availableWidth/100, data) )
                    .tickSize( -availableHeight , 0);

                g.select(".nv-x.nv-axis")
                    .attr("transform", "translate(0," + y.range()[0] + ")")
                    .call(xAxis);
            }

            if (showYAxis) {
                yAxis
                    .scale(y)
                    ._ticks( nv.utils.calcTicksY(availableHeight/36, data) )
                    .tickSize( -availableWidth, 0);

                g.select(".nv-y.nv-axis")
                    .call(yAxis);
            }

            //============================================================
            // Event Handling/Dispatching (in chart"s scope)
            //------------------------------------------------------------

            legend.dispatch.on("stateChange", function(newState) {
                for (var key in newState)
                    state[key] = newState[key];
                dispatch.stateChange(state);
                chart.update();
            });

            // Update chart from a state object passed to event handler
            dispatch.on("changeState", function(e) {
                if (typeof e.disabled !== "undefined") {
                    data.forEach(function(series,i) {
                        series.disabled = e.disabled[i];
                    });
                    state.disabled = e.disabled;
                }
                chart.update();
            });

            var tip = d3.tip()
                .attr("class", "tip")
                .html(function(d) {
                    return contentGenerator(d);
                });

            var points = d3.select(this).selectAll("circle.nv-point");

            points.each(function(d) {
                d3.select(this).call(tip);
            });

            points
                .on("mouseenter", function(d, i){
                    tip.show(d, i);
                })
                .on("mouseleave", tip.hide);


            // store old scales for use in transitions on update
            x0 = x.copy();
            y0 = y.copy();

        });

        renderWatch.renderEnd("scatter with line immediate");
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    // expose chart"s sub-components
    chart.dispatch = dispatch;
    chart.scatter = scatter;
    chart.legend = legend;
    chart.xAxis = xAxis;
    chart.yAxis = yAxis;
    chart.distX = distX;
    chart.distY = distY;

    chart.options = nv.utils.optionsFunc.bind(chart);
    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        contentGenerator: {
            get: function(){return contentGenerator;},
            set: function(_){contentGenerator=_; }
        },
        width: {get: function(){return width;}, set: function(_){width=_;}},
        height:     {get: function(){return height;}, set: function(_){height=_;}},
        container:  {get: function(){return container;}, set: function(_){container=_;}},
        showDistX:  {get: function(){return showDistX;}, set: function(_){showDistX=_;}},
        showDistY:  {get: function(){return showDistY;}, set: function(_){showDistY=_;}},
        showLegend: {get: function(){return showLegend;}, set: function(_){showLegend=_;}},
        showXAxis:  {get: function(){return showXAxis;}, set: function(_){showXAxis=_;}},
        showYAxis:  {get: function(){return showYAxis;}, set: function(_){showYAxis=_;}},
        defaultState:     {get: function(){return defaultState;}, set: function(_){defaultState=_;}},
        noData:     {get: function(){return noData;}, set: function(_){noData=_;}},
        duration:   {get: function(){return duration;}, set: function(_){duration=_;}},

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = _.top    !== undefined ? _.top    : margin.top;
            margin.right  = _.right  !== undefined ? _.right  : margin.right;
            margin.bottom = _.bottom !== undefined ? _.bottom : margin.bottom;
            margin.left   = _.left   !== undefined ? _.left   : margin.left;
        }},
        rightAlignYAxis: {get: function(){return rightAlignYAxis;}, set: function(_){
            rightAlignYAxis = _;
            yAxis.orient( (_) ? "right" : "left");
        }},
        color: {get: function(){return color;}, set: function(_){
            color = nv.utils.getColor(_);
            legend.color(color);
            distX.color(color);
            distY.color(color);
        }}
    });

    nv.utils.inheritOptions(chart, scatter);
    nv.utils.initOptions(chart);
    return chart;
};


module.exports = {
    scatter_chart: scatter_chart
}
