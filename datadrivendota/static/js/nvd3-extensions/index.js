'use strict';

var nvd3 = window.nv;

nvd3.extensions = {};
nvd3.extensions.charts = require('./charts');
nvd3.extensions.utils = require('./utils');
nvd3.extensions.models = require('./models');
nvd3.extensions.components = require('./components');


module.exports = nvd3;
