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
          "datadrivendota/static/css/custom_nvd3_compilation.css": "datadrivendota/static/css/custom_nvd3_compilation.less",
        }
      }
    },
    cssmin: {
      target: {
        files: {
          'datadrivendota/static/css/release.css': [
            'datadrivendota/static/css/custom_nvd3_compilation.css',
            'datadrivendota/static/css/custom_bootstrap_compilation.css',
            'datadrivendota/static/css/dota2minimapheroes.css',
            'datadrivendota/static/css/icons_png.css',
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

  grunt.registerTask('default', ['less', 'cssmin', 'watch']);
};
