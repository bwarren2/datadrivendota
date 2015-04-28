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
        // NOTE: changing the subfiles of project.css does not trigger recompilation!
      }
    },
    watch: {
      styles: {
        files: ['datadrivendota/static/css/*.less'], // which files to watch
        tasks: ['less'],
        options: {
          nospawn: true
        }
      }
    }
  });

  grunt.registerTask('default', ['less', 'watch']);
};
