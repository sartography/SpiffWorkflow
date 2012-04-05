/*
    json.js
    2006-04-28
    2006-05-27 added prettyPrint argument

    This file adds these methods to JavaScript:

        object.toJSONString(prettyPrint)

            This method produces a JSON text from an object. The
            object must not contain any cyclical references.

        array.toJSONString(prettyPrint)

            This method produces a JSON text from an array. The
            array must not contain any cyclical references.

        string.parseJSON()

            This method parses a JSON text to produce an object or
            array. It will return false if there is an error.

+           added prettyPrint argument
            prettyPrint ... if set to true the resulting string will be formated
                            with tabs and returns to be more human readable.
                            by Matthias.Platzer@knallgrau.at

*/
(function () {
    var INTEND = "\t";
    var NEWLINE = "\n";
    var pPr = true;
    var intendLevel = 0;
    var intend = function(a) {
        if (!pPr) return a;
        for (var l=0; l<intendLevel; l++) {
            a[a.length] = INTEND;
        }
        return a;
    };

    var newline = function(a) {
        if (pPr) a[a.length] = NEWLINE;
        return a;
    };

    var m = {
            '\b': '\\b',
            '\t': '\\t',
            '\n': '\\n',
            '\f': '\\f',
            '\r': '\\r',
            '"' : '\\"',
            '\\': '\\\\'
        },
        s = {
            array: function (x) {
                var a = ['['], b, f, i, l = x.length, v;
                a = newline(a);
                intendLevel++;
                for (i = 0; i < l; i += 1) {
                    v = x[i];
                    f = s[typeof v];
                    if (f) {
                        v = f(v);
                        if (typeof v == 'string') {
                            if (b) {
                                a[a.length] = ',';
                                a = newline(a);
                            }
                            a = intend(a);
                            a[a.length] = v;
                            b = true;
                        }
                    }
                }
                intendLevel--;
                a = newline(a);
                a = intend(a);
                a[a.length] = ']';
                return a.join('');
            },
            'boolean': function (x) {
                return String(x);
            },
            'null': function (x) {
                return "null";
            },
            number: function (x) {
                return isFinite(x) ? String(x) : 'null';
            },
            object: function (x, formatedOutput) {
                if (x) {
                    if (x instanceof Array) {
                        return s.array(x);
                    }
                    var a = ['{'], b, f, i, v;
                    a = newline(a);
                    intendLevel++;
                    for (i in x) {
                        v = x[i];
                        f = s[typeof v];
                        if (f) {
                            v = f(v);
                            if (typeof v == 'string') {
                                if (b) {
                                    a[a.length] = ',';
                                    a = newline(a);
                                }
                                a = intend(a);
                                a.push(s.string(i), ((pPr) ? ' : ' : ':'), v);
                                b = true;
                            }
                        }
                    }
                    intendLevel--;
                    a = newline(a);
                    a = intend(a);
                    a[a.length] = '}';
                    return a.join('');
                }
                return 'null';
            },
            string: function (x) {
                if (/["\\\x00-\x1f]/.test(x)) {
                    x = x.replace(/([\x00-\x1f\\"])/g, function(a, b) {
                        var c = m[b];
                        if (c) {
                            return c;
                        }
                        c = b.charCodeAt();
                        return '\\u00' +
                            Math.floor(c / 16).toString(16) +
                            (c % 16).toString(16);
                    });
                }
                return '"' + x + '"';
            }
        };

    Object.prototype.toPrettyJSONString = function () {
        //pPr = prettyPrint;
        return s.object(this);
    };

    Array.prototype.toPrettyJSONString = function () {
        //pPr = prettyPrint;
        return s.array(this);
    };
})();