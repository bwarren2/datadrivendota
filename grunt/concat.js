"use strict";
module.exports = {
    options: {
        separator: ';\n'
    },
    dist: {
        src: [
            "bower_components/jquery/dist/jquery.min.js",
            "bower_components/messenger/build/js/messenger.min.js",
            "bower_components/messenger/build/js/messenger-theme-future.js",
            "bower_components/bootstrap/js/transition.js",
            "bower_components/bootstrap/js/modal.js",
            "bower_components/bootstrap/js/dropdown.js",
            "bower_components/bootstrap/js/scrollspy.js",
            "bower_components/bootstrap/js/tab.js",
            "bower_components/bootstrap/js/tooltip.js",
            "bower_components/bootstrap/js/popover.js",
            "bower_components/bootstrap/js/alert.js",
            "bower_components/bootstrap/js/button.js",
            "bower_components/bootstrap/js/collapse.js",
            "bower_components/bootstrap/js/carousel.js",
            "bower_components/bootstrap/js/affix.js",
            "bower_components/d3/d3.min.js",
            "bower_components/jqueryui/jquery-ui.min.js",
            "bower_components/nvd3/build/nv.d3.min.js",
            "bower_components/handlebars/handlebars.min.js",
            "bower_components/eldarion-ajax/js/eldarion-ajax.min.js",
            "bower_components/sprintf/dist/sprintf.min.js",
            "bower_components/select2/dist/js/select2.js",
            "bower_components/moment/min/moment.min.js",
            "bower_components/lodash/lodash.min.js",
            "bower_components/clipboard/dist/clipboard.min.js",
            "js/charting.js",
            "js/project.js",
            "js/plotly1.9.0.min.js",
        ].map(function(file) { return "datadrivendota/static/" + file; }),
      dest: "datadrivendota/static/dist/built.js",
    },
};
