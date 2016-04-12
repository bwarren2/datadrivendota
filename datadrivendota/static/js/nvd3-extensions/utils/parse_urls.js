"use strict";


if (!String.prototype.format) {
  String.prototype.format = function() {
    var args = arguments;
    return this.replace(/{(\d+)}/g, function(match, number) {
      return typeof args[number] != "undefined" ? args[number] : match;
    });
  };
};

var version = 2;
var parse_url = "https://s3.amazonaws.com/datadrivendota/processed_replay_parse/";

// https://s3.amazonaws.com/datadrivendota/processed_replay_parse/2107579100_130_combatlog_item_buys_v1.json.gz
var url_for = function(shard, facet, logtype){
    return parse_url+"{0}_{1}_{2}_{3}_v{4}.json.gz".format(
        shard.match_id, shard.dataslice, logtype, facet, version
    );
};

module.exports = {
    url_for: url_for,
}
