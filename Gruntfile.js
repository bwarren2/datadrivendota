module.exports = function(grunt) {
  require('jit-grunt')(grunt);

  grunt.initConfig({
    less: {
      development: {
        options: {
          compress: true,
          yuicompress: true,
          optimization: 2
        },
        files: {
          "datadrivendota/static/css/custom_bootstrap_compilation.css":
          "datadrivendota/static/css/custom_bootstrap_compilation.less",
          "datadrivendota/static/css/project.css": "datadrivendota/static/css/project.less",
          "datadrivendota/static/css/bootstrap-tour.css": "datadrivendota/static/css/bootstrap-tour.less",
          "datadrivendota/static/css/variables.css": "datadrivendota/static/css/variables.less",
        }
      }
    },
    cssmin: {
    options: {
      shorthandCompacting: false,
      roundingPrecision: -1
    },
    target: {
      files: {
        'datadrivendota/static/css/release.css': [
          'datadrivendota/static/css/custom_bootstrap_compilation.css',
          'datadrivendota/static/css/dota2minimapheroes.css',
          'datadrivendota/static/css/icons_png.css',
          'datadrivendota/static/css/bootstrap-tour.css',
          'datadrivendota/static/jquery-ui-bootstrap/jquery-ui-1.10.0.custom.css',
          'datadrivendota/static/select2-3.4.5/select2.css',
          'datadrivendota/static/select2-3.4.5/select2-bootstrap.css',
          'datadrivendota/static/messenger/messenger.css',
          'datadrivendota/static/messenger/messenger-theme-future.css',
          'datadrivendota/static/css/project.css'
        ]
      }
    }
  },
    watch: {
      styles: {
        files: [
          'datadrivendota/static/css/*.less',
          'datadrivendota/static/css/project/*.less'
        ], // which files to watch
        tasks: ['less', 'cssmin'],
        options: {
          nospawn: true
        }
      }
    }
  });

  grunt.registerTask('default', ['less', 'watch']);
};
