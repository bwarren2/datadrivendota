(function(f){if(typeof exports==="object"&&typeof module!=="undefined"){module.exports=f()}else if(typeof define==="function"&&define.amd){define([],f)}else{var g;if(typeof window!=="undefined"){g=window}else if(typeof global!=="undefined"){g=global}else if(typeof self!=="undefined"){g=self}else{g=this}g.binky = f()}})(function(){var define,module,exports;return (function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
"use strict"

function formatPms (log) {
  if (log.loading) return "";

  var markup = "<div class='select2-result-log clearfix'>" +
    // "<div class='select2-result-pms__avatar'><img src='" + pms.hero.image_url + "' /></div>" +
    "<div class='select2-result-pms__meta'>" +
      "<div class='select2-result-pms__title'>" + log.hero.name+", M#"+log.match.steam_id + "</div>"+
      "</div></div>";

  return markup;
}

function formatPmsSelection (log) {
  return log.hero.name+', M#'+log.match.steam_id;
}


var pms_select2 = function(selector){

    $(selector).select2({
      ajax: {
        url: "/rest-api/player-match-summary/",
        dataType: 'json',
        delay: 250,
        multiple: true,
        data: function (params) {
          return {
            match_id: params.term, // search term
            page: params.page
          };
        },
        processResults: function (data, params) {
          params.page = params.page || 1;

          return {
            // If you don't provide an id, the select is disabled by default.
            results: data,
            pagination: {
              more: (params.page * 30) < data.total_count
            }
          };
        },
        cache: true
      },
      escapeMarkup: function (markup) { return markup; },
      minimumInputLength: 6,
      templateResult: formatPms,
      templateSelection: formatPmsSelection

    });
    console.log('Did it');
}

frontend = {};
frontend.inputs = {};
frontend.inputs.pms_select2 = pms_select2;

module.exports = {
    frontend: frontend
}

},{}]},{},[1])(1)
});