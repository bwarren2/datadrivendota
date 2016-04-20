"use strict";

function AjaxCache() {
    this.cache = {};
}

AjaxCache.prototype.get = function (path) {
    var self = this;  // Just in case the Promise.resolve call screws with `this`.
    if (self.cache.hasOwnProperty(path)) {
        return Promise.resolve(self.cache[path]);
    } else {
        self.cache[path] = $.ajax(path);
        return self.cache[path];
    }
}

var aj = new AjaxCache();

module.exports = aj;
