module.exports = {
  development: {
    options: {
      compress: true,
      yuicompress: true,
      optimization: 2,
    },
    files: {
      "datadrivendota/static/css/custom_bootstrap_compilation.css":
      "datadrivendota/static/css/custom_bootstrap_compilation.less",
      "datadrivendota/static/css/project.css": "datadrivendota/static/css/project.less",
      "datadrivendota/static/css/bootstrap-tour.css": "datadrivendota/static/css/bootstrap-tour.less",
      "datadrivendota/static/css/variables.css": "datadrivendota/static/css/variables.less",
      "datadrivendota/static/css/nvd3_custom_compilation.css": "datadrivendota/static/css/nvd3_custom_compilation.less",
    }
  }
}
