"use strict";
module.exports = {
     options: {
      // Task-specific options go here.
    },
    all: {
        src: [
            "bower_components/messenger/build/css/messenger.css",
            "bower_components/messenger/build/css/messenger-theme-future.css",
            "bower_components/select2/dist/css/select2.css",
            "bower_components/jqueryui/themes/smoothness/jquery-ui.min.css",
            "css/nvd3_custom_compilation.css",
        ].map(function(filename){return "datadrivendota/static/"+filename;}),
        dest: "datadrivendota/static/dist/styles.css"
    },
}
