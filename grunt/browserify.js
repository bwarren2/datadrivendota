module.exports = {
    js: {
        // A single entry point for our app
        src: 'datadrivendota/static/js/nvd3-extensions/index.js',
        // Compile to a single file to add a script tag for in your HTML
        dest: 'datadrivendota/static/js/d7.js',
        options: {
          browserifyOptions: {
            standalone: 'd7'
          },
        }
    },
    frontend: {
        // A single entry point for our app
        src: 'datadrivendota/static/js/frontend/index.js',
        // Compile to a single file to add a script tag for in your HTML
        dest: 'datadrivendota/static/js/frontend.js',
        options: {
          browserifyOptions: {
            standalone: 'frontend'
          },
        }
    },
}
