'use strict';

var d3 = require('../../bower_components/d3/d3.js');
var nvd3 = require('../../bower_components/nvd3/build/nv.d3.js');


nvd3.extensions = {};
nvd3.extensions.charts = require('./charts')
nvd3.extensions.utils = require('./utils')
nvd3.extensions.models = require('./models')
nvd3.extensions.components = require('./components')


module.exports = nvd3;
