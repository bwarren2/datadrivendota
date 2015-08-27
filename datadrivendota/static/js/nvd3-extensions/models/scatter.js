'use strict';
var d3 = window.d3;
var utils = require('../utils');

var scatter = function() {

    //============================================================
    // Public Variables with Default Settings
    //------------------------------------------------------------

    // Config
    var margin       = {top: 0, right: 0, bottom: 0, left: 0};
    var width        = null;
    var height       = null;
    var color        = nv.utils.defaultColor();  // chooses color
    var id           = Math.floor(Math.random() * 100000);  // Create semi-unique ID incase user doesn't select one
    var container    = null;

    // Scales
    var x = d3.scale.linear();
    var y = d3.scale.linear();
    var z = d3.scale.linear(); //linear b/c d3.svg.shape.size is treated as area


    // Accessors to data
    var getX         = function(d) { return d.x; };
    var getY         = function(d) { return d.y; };
    var getSize      = function(d) { return d.size || 1; };
    var getShape     = function(d) { return d.shape || 'circle'; };

    // Interactivity config
    var interactive  = true; // If true, plots a voronoi overlay for advanced point intersection
    var pointActive  = function(d) { return !d.notActive }; // any points that return false will be filtered out
    var padData      = false; // If true, adds half a data points width to front and back, for lining up a line chart with a bar chart
    var padDataOuter = .1; //outerPadding to imitate ordinal scale outer padding
    var clipEdge     = false; // if true, masks points within x and y scale
    var clipVoronoi  = true; // if true, masks each point with a circle... can turn off to slightly increase performance
    var showVoronoi  = false; // display the voronoi areas
    var clipRadius   = function() { return 25 }; // function to get the radius for voronoi point clips

    // Overrides
    var xDomain      = null;
    var yDomain      = null;
    var xRange       = null;
    var yRange       = null;
    var sizeDomain   = null; // Override point size domain
    var forceX       = []; // (ie. 0, or a max / min, etc.)
    var forceY       = [];
    var forceSize    = [];

    var sizeRange    = null;
    var singlePoint  = false;
    var dispatch     = d3.dispatch(
        'elementClick',
        'elementDblClick',
        'elementMouseover',
        'elementMouseout',
        'renderEnd'
    );
    var useVoronoi   = true;
    var duration     = 250;


    //============================================================
    // Private Variables
    //------------------------------------------------------------

    var timeoutID
    var needsUpdate = false // Flag for when the points are visually updating, but the interactive layer is behind, to disable tooltips
    var renderWatch = nv.utils.renderWatch(dispatch, duration)
    var _sizeRange_def = [16, 256]
        ;

    var chart = function(selection) {
        renderWatch.reset();
        selection.each(function(data) {
            container = d3.select(this);
            var availableWidth = nv.utils.availableWidth(
                width, container, margin
            );
            var availableHeight = nv.utils.availableHeight(
                height, container, margin
            );

            nv.utils.initSVG(container);

            //add series index to each data point for reference
            data.forEach(function(series, i) {
                series.values.forEach(function(point) {
                    point.series = i;
                });
            });

            // Setup Scales
            // remap and flatten the data for use in calculating the scales' domains
            var seriesData = (xDomain && yDomain && sizeDomain) ? [] : // if we know xDomain and yDomain and sizeDomain, no need to calculate.... if Size is constant remember to set sizeDomain to speed up performance
                d3.merge(
                    data.map(function(d) {
                        return d.values.map(function(d,i) {
                            return {x: getX(d), y: getY(d), size: getSize(d)};
                        });
                    })
                );

            x.domain(
                xDomain || d3.extent(
                    seriesData.map(function(d) { return d.x; }).concat(forceX)
                )
            );

            if (padData && data[0])
                x.range(xRange || [(availableWidth * padDataOuter +  availableWidth) / (2 *data[0].values.length), availableWidth - availableWidth * (1 + padDataOuter) / (2 * data[0].values.length)  ]);
            //x.range([availableWidth * .5 / data[0].values.length, availableWidth * (data[0].values.length - .5)  / data[0].values.length ]);
            else
                x.range(xRange || [0, availableWidth]);

            y.domain(
                yDomain || d3.extent(
                    seriesData.map(function(d) { return d.y; }).concat(forceY)
                )
            ).range(yRange || [availableHeight, 0]);

            z.domain(
                sizeDomain || d3.extent(
                    seriesData.map(function(d) { return d.size; }).concat(forceSize)
                    )
                ).range(sizeRange || _sizeRange_def);

            // If scale's domain don't have a range, slightly adjust to make one... so a chart can show a single data point
            singlePoint = x.domain()[0] === x.domain()[1] || y.domain()[0] === y.domain()[1];

            if (x.domain()[0] === x.domain()[1])
                x.domain()[0] ?
                    x.domain([x.domain()[0] - x.domain()[0] * 0.01, x.domain()[1] + x.domain()[1] * 0.01])
                    : x.domain([-1,1]);

            if (y.domain()[0] === y.domain()[1])
                y.domain()[0] ?
                    y.domain([y.domain()[0] - y.domain()[0] * 0.01, y.domain()[1] + y.domain()[1] * 0.01])
                    : y.domain([-1,1]);

            if ( isNaN(x.domain()[0])) {
                x.domain([-1,1]);
            }

            if ( isNaN(y.domain()[0])) {
                y.domain([-1,1]);
            }


            // Setup containers and skeleton of chart
            var wrap = container.selectAll('g.nv-wrap.nv-scatter').data([data]);

            var wrapEnter = wrap.enter().append('g').attr(
                'class', 'nvd3 nv-wrap nv-scatter nv-chart-' + id
            );

            var defsEnter = wrapEnter.append('defs');
            var gEnter = wrapEnter.append('g');
            var g = wrap.select('g');

            wrap.classed('nv-single-point', singlePoint);
            gEnter.append('g').attr('class', 'nv-groups');
            gEnter.append('g').attr('class', 'nv-point-paths');
            wrapEnter.append('g').attr('class', 'nv-point-clips');

            wrap.attr(
                'transform',
                'translate(' + margin.left + ',' + margin.top + ')'
            );

            defsEnter.append('clipPath')
                .attr('id', 'nv-edge-clip-' + id)
                .append('rect');

            wrap.select('#nv-edge-clip-' + id + ' rect')
                .attr('width', availableWidth)
                .attr('height', (availableHeight > 0) ? availableHeight : 0);

            g.attr(
                'clip-path', clipEdge ? 'url(#nv-edge-clip-' + id + ')' : ''
            );

            needsUpdate = true;


            // Create groups
            var groups = wrap.select('.nv-groups').selectAll('.nv-group')
                .data(
                    function(d) { return d; },
                    function(d) { return d.key; }
                );

            groups.enter().append('g')
                .style('stroke-opacity', 1e-6)
                .style('fill-opacity', 1e-6);

            groups
                .exit()
                .remove();

            groups
                .attr(
                    'class',
                    function(d,i) { return 'nv-group nv-series-' + i; }
                )
                .classed('hover', function(d) { return d.hover; });

            groups.watchTransition(renderWatch, 'scatter: groups')
                .style('fill', function(d,i) { return color(d, i); })
                .style('stroke', function(d,i) { return color(d, i); })
                .style('stroke-opacity', 1)
                .style('fill-opacity', 0.5);


            // create points, maintaining their IDs from the original data set
            var points = groups.selectAll('circle.nv-point')
                .data(function(d) {
                    return d.values.map(
                        function (point, pointIndex) {
                            return [point, pointIndex];
                        }).filter(
                            function(pointArray, pointIndex) {
                                return pointActive(pointArray[0], pointIndex);
                            });
                    });

            points
                .enter()
                .append('circle')
                .attr('cx', function(d){return x(getX(d[0])).toFixed(2);})
                .attr('cy', function(d){return y(getY(d[0])).toFixed(2);})
                .attr('r', function(d){return 5;});

            points.each(function(d) {
                d3.select(this)
                    .classed('nv-point', true)
                    .classed('nv-point-doctor', true)
                    .classed('nv-point-' + d[1], true)
                    .classed('nv-noninteractive', !interactive)
                    .classed('hover', false)
                ;
            });

            points
                .watchTransition(renderWatch, 'scatter points')
                .attr('cx', function(d){ return x(getX(d[0]));})
                .attr('cy', function(d){ return y(getY(d[0]));});


            // Handle exits
            points
                .exit()
                .remove();

            groups
                .exit()
                .selectAll('circle.nv-point')
                .watchTransition(renderWatch, 'scatter exit')
                .attr(
                    'transform',
                    function(d) {
                        return 'translate(' + x(getX(d[0])) + ',' + y(getY(d[0])) + ')';
                })
                .remove();

        });
        renderWatch.renderEnd('scatter immediate');
        return chart;
    }

    //============================================================
    // Expose Public Variables
    //------------------------------------------------------------

    chart.dispatch = dispatch;
    chart.options = nv.utils.optionsFunc.bind(chart);

    // utility function calls provided by this chart
    chart._calls = {
        clearHighlights: function () {
            nv.dom.write(function() {
                container.selectAll('.nv-point.hover').classed('hover', false);
            });
            return null;
        },
        highlightPoint: function (seriesIndex, pointIndex, isHoverOver) {
            nv.dom.write(function() {
                container.select('.nv-groups')
                  .selectAll('.nv-series-' + seriesIndex)
                  .selectAll('.nv-point-' + pointIndex)
                  .classed('hover', isHoverOver);
            });
        }
    };

    // trigger calls from events too
    dispatch.on('elementMouseover.point', function(d) {
        if (interactive){
            chart._calls.highlightPoint(d.seriesIndex,d.pointIndex,true);
        }
    });

    dispatch.on('elementMouseout.point', function(d) {
        if (interactive){
            chart._calls.highlightPoint(d.seriesIndex,d.pointIndex,false);
        }
    });

    chart._options = Object.create({}, {
        // simple options, just get/set the necessary values
        // width:   utils.getSet(width),

        width: {get: function(){return width;}, set: function(_){width=_;}},
        height: {get: function(){return height;}, set: function(_){height=_;}},
        xScale: {get: function(){return x;}, set: function(_){x=_;}},
        yScale: {get: function(){return y;}, set: function(_){y=_;}},
        pointScale: {get: function(){return z;}, set: function(_){z=_;}},
        xDomain: {
            get: function(){return xDomain;},
            set: function(_){xDomain=_;}
        },
        yDomain: {
            get: function(){return yDomain;},
            set: function(_){yDomain=_;}
        },
        pointDomain: {
            get: function(){return sizeDomain;},
            set: function(_){sizeDomain=_;}
        },
        xRange: {get: function(){return xRange;}, set: function(_){xRange=_;}},
        yRange: {get: function(){return yRange;}, set: function(_){yRange=_;}},
        pointRange: {
            get: function(){return sizeRange;},
            set: function(_){sizeRange=_;}
        },
        forceX: {get: function(){return forceX;}, set: function(_){forceX=_;}},
        forceY: {get: function(){return forceY;}, set: function(_){forceY=_;}},
        forcePoint: {
            get: function(){return forceSize;},
            set: function(_){forceSize=_;}
        },
        interactive: {
            get: function(){return interactive;},
            set: function(_){interactive=_;}
        },
        pointActive: {
            get: function(){return pointActive;},
            set: function(_){pointActive=_;}
        },
        padDataOuter:{
            get: function(){return padDataOuter;},
            set: function(_){padDataOuter=_;}
        },
        padData: {
            get: function(){return padData;},
            set: function(_){padData=_;}
        },
        clipEdge: {
            get: function(){return clipEdge;},
            set: function(_){clipEdge=_;}
        },
        clipVoronoi: {
            get: function(){return clipVoronoi;},
            set: function(_){clipVoronoi=_;}
        },
        clipRadius: {
            get: function(){return clipRadius;},
            set: function(_){clipRadius=_;}
        },
        showVoronoi: {
            get: function(){return showVoronoi;},
            set: function(_){showVoronoi=_;}
        },
        id: {get: function(){return id;}, set: function(_){id=_;}},


        // simple functor options
        x: {
            get: function(){return getX;},
            set: function(_){getX = d3.functor(_);}
        },
        y: {
            get: function(){return getY;},
            set: function(_){getY = d3.functor(_);}
        },
        pointSize: {
            get: function(){return getSize;},
            set: function(_){getSize = d3.functor(_);}
        },
        pointShape: {
            get: function(){return getShape;},
            set: function(_){getShape = d3.functor(_);}
        },

        // options that require extra logic in the setter
        margin: {get: function(){return margin;}, set: function(_){
            margin.top    = _.top    !== undefined ? _.top    : margin.top;
            margin.right  = _.right  !== undefined ? _.right  : margin.right;
            margin.bottom = _.bottom !== undefined ? _.bottom : margin.bottom;
            margin.left   = _.left   !== undefined ? _.left   : margin.left;
        }},
        duration: {
            get: function(){return duration;},
            set: function(_){
                duration = _;
                renderWatch.reset(duration);
            }
        },
        color: {
            get: function(){return color;},
            set: function(_){
                color = nv.utils.getColor(_);
            }
        },
        useVoronoi: {
            get: function(){return useVoronoi;},
            set: function(_){
                useVoronoi = _;
                if (useVoronoi === false) {
                    clipVoronoi = false;
                }
            }
        }
    });
    utils.initOptions(chart);
    return chart;
};

module.exports = {
    scatter: scatter
}
