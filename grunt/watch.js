module.exports = {
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
