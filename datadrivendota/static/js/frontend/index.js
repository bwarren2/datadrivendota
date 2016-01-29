"use strict"

var Foo = window.Foo || {};

Foo.baz = 2;

// window.Foo = Foo;

module.exports = {
    Foo: Foo
}
