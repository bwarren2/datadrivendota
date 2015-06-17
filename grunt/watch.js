"use strict";
module.exports = {
    styles: {
      files: [
        "datadrivendota/static/css/*.less",
        "datadrivendota/static/css/project/*.less"
      ], // which files to watch
      tasks: ["less", "cssmin"],
      options: {
        nospawn: true
      }
    },
    js: {
      files: [
        "js/*.js",
        "bower_components/**/*.js",
      ].map(function(filename){return "datadrivendota/static/"+filename;}),
      tasks: ["concat"],
      options: {
        nospawn: true
      }
    }
}
