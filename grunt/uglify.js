module.exports = {
    all: {
        files: [{
            expand: true,
            cwd: 'datadrivendota/static',
            src: ['bower_components/jquery/dist/jquery.min.js',
            'bower_components/messenger/build/js/messenger.min.js',
            'bower_components/messenger/build/js/messenger-theme-future.js',
            'bower_components/bootstrap/js/transition.js',
            'bower_components/bootstrap/js/modal.js',
            'bower_components/bootstrap/js/dropdown.js',
            'bower_components/bootstrap/js/scrollspy.js',
            'bower_components/bootstrap/js/tab.js',
            'bower_components/bootstrap/js/tooltip.js',
            'bower_components/bootstrap/js/popover.js',
            'bower_components/bootstrap/js/alert.js',
            'bower_components/bootstrap/js/button.js',
            'bower_components/bootstrap/js/collapse.js',
            'bower_components/bootstrap/js/carousel.js',
            'bower_components/bootstrap/js/affix.js',
            'bower_components/d3/d3.min.js',
            'bower_components/jqueryui/jquery-ui.min.js',
            'bower_components/nvd3/build/nv.d3.min.js',
            'bower_components/bluebird/js/browser/bluebird.min.js',
            'bower_components/handlebars/handlebars.min.js',
            'js/eldarion-ajax.js',
            'js/charting.js',
            'js/project.js',
            'bower_components/select2/dist/js/select2.min.js',
            ],
            dest: 'datadrivendota/static/js',
            ext: '.min.js'
        }]
    }
};
