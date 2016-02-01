"use strict";


if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != "undefined" ? args[number] : match;
    });
  };
};

var version = 1;
var parse_url = "https://s3.amazonaws.com/datadrivendota/processed_replay_parse/";

var url_for = function(pms, facet, logtype){
    return parse_url+"{0}_{3}_{1}_v{2}.json.gz".format(
        pms.lookup_pair, facet, version, logtype
    );
};

module.exports = {
    url_for: url_for,
}