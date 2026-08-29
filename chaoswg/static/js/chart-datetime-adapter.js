/* global Chart */
/**
 * Minimal date adapter for Chart.js 4 time scales.
 *
 * Replaces the deprecated chartjs-adapter-moment (and with it the moment.js
 * CDN script): dates are parsed with native Date and tick labels are
 * formatted with a small moment-style token set. No external libraries.
 *
 * The JSON endpoints send HTTP-date strings (e.g. "Wed, 29 Aug 2026
 * 21:00:00 GMT", what Flask's jsonify produces for datetime objects) or
 * ISO-8601 strings; both are handled.
 *
 * Must be loaded AFTER chart.umd.min.js and BEFORE the page's chart script.
 */
(function () {
    'use strict';

    if (typeof Chart === 'undefined' || !Chart._adapters || !Chart._adapters._date) {
        /* eslint-disable no-console */
        console.warn('chart-datetime-adapter: Chart.js not loaded?');
        /* eslint-enable no-console */
        return;
    }

    var MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    // Longest match first (YYYY before YY, MMMM before MMM, ...)
    var TOKENS = /(YYYY|YY|MMMM|MMM|MM|DD|HH|hh|mm|ss|SSS|A|a|M|D|H|h|m|s)/g;

    function pad(n, width) {
        return ('000000' + n).slice(-width);
    }

    /**
     * Parse a number, Date, ISO-8601 or HTTP-date (RFC 1123) string to
     * epoch milliseconds. Returns null when unparseable.
     */
    function parse(value) {
        if (value == null || value === '') return null;
        if (typeof value === 'number') return isFinite(value) ? value : null;
        if (value instanceof Date) return isNaN(value) ? null : +value;
        if (typeof value === 'string') {
            var t = Date.parse(value);
            if (!isNaN(t)) return t;
            // Fallback for HTTP dates such as "Wed, 29 Aug 2026 21:00:00 GMT"
            var m = value.match(/^\s*\w{3,9}\s*,?\s*(\d{1,2})\s+(\w{3})\s+(\d{2,4})\s+(\d{1,2}):(\d{2}):(\d{2})\s*(\S*)$/);
            if (m) {
                var mi = MONTHS.indexOf(m[2].slice(0, 3).toUpperCase());
                if (mi !== -1) {
                    var year = parseInt(m[3], 10);
                    if (year < 100) year += year < 70 ? 2000 : 1900;
                    var day = parseInt(m[1], 10),
                        hour = parseInt(m[4], 10),
                        minute = parseInt(m[5], 10),
                        second = parseInt(m[6], 10);
                    var zone = (m[7] || '').toUpperCase();
                    if (zone === '' || zone === 'GMT' || zone === 'UTC') {
                        return +new Date(Date.UTC(year, mi, day, hour, minute, second));
                    }
                    var tz = m[7].match(/^([+-])(\d{2}):?(\d{2})$/);
                    if (tz) {
                        var offset = (tz[1] === '+' ? 1 : -1) *
                            (parseInt(tz[2], 10) * 60 + parseInt(tz[3], 10)) * 60000;
                        return +new Date(Date.UTC(year, mi, day, hour, minute, second) - offset);
                    }
                }
            }
        }
        return null;
    }

    /** Format epoch milliseconds with moment-style tokens (DD.MM.YY, HH:mm, ...). */
    function format(time, formatString) {
        var d = new Date(time);
        if (formatString == null) formatString = 'DD.MM.YY';
        var shortMonth = d.toLocaleDateString(undefined, { month: 'short' });
        var longMonth = d.toLocaleDateString(undefined, { month: 'long' });
        return String(formatString).replace(TOKENS, function (tok) {
            switch (tok) {
                case 'YYYY': return pad(d.getFullYear(), 4);
                case 'YY':   return pad(d.getFullYear() % 100, 2);
                case 'MMMM': return longMonth;
                case 'MMM':  return shortMonth;
                case 'MM':   return pad(d.getMonth() + 1, 2);
                case 'M':    return d.getMonth() + 1;
                case 'DD':   return pad(d.getDate(), 2);
                case 'D':    return d.getDate();
                case 'HH':   return pad(d.getHours(), 2);
                case 'H':    return d.getHours();
                case 'hh':   return pad(d.getHours() % 12 || 12, 2);
                case 'h':    return d.getHours() % 12 || 12;
                case 'mm':   return pad(d.getMinutes(), 2);
                case 'm':    return d.getMinutes();
                case 'ss':   return pad(d.getSeconds(), 2);
                case 's':    return d.getSeconds();
                case 'SSS':  return pad(d.getMilliseconds(), 3);
                case 'A':    return d.getHours() < 12 ? 'AM' : 'PM';
                case 'a':    return d.getHours() < 12 ? 'am' : 'pm';
                default:     return tok;
            }
        });
    }

    function add(time, amount, unit) {
        var d = new Date(time);
        switch (unit) {
            case 'millisecond': d.setMilliseconds(d.getMilliseconds() + amount); break;
            case 'second':      d.setSeconds(d.getSeconds() + amount); break;
            case 'minute':      d.setMinutes(d.getMinutes() + amount); break;
            case 'hour':        d.setHours(d.getHours() + amount); break;
            case 'day':         d.setDate(d.getDate() + amount); break;
            case 'week':
            case 'isoWeek':     d.setDate(d.getDate() + 7 * amount); break;
            case 'month':       d.setMonth(d.getMonth() + amount); break;
            case 'quarter':     d.setMonth(d.getMonth() + 3 * amount); break;
            case 'year':        d.setFullYear(d.getFullYear() + amount); break;
            default: throw new Error('chart-datetime-adapter: unknown unit "' + unit + '"');
        }
        return +d;
    }

    function diff(a, b, unit) {
        var x = new Date(a), y = new Date(b);
        switch (unit) {
            case 'millisecond': return x - y;
            case 'second':      return Math.trunc((x - y) / 1000);
            case 'minute':      return Math.trunc((x - y) / 60000);
            case 'hour':        return Math.trunc((x - y) / 3600000);
            case 'day':         return Math.trunc((x - y) / 86400000);
            case 'week':
            case 'isoWeek':     return Math.trunc((x - y) / 604800000);
            case 'month':       return (x.getFullYear() - y.getFullYear()) * 12 +
                                       x.getMonth() - y.getMonth();
            case 'quarter':     return (x.getFullYear() - y.getFullYear()) * 4 +
                                       Math.floor(x.getMonth() / 3) - Math.floor(y.getMonth() / 3);
            case 'year':        return x.getFullYear() - y.getFullYear();
            default: throw new Error('chart-datetime-adapter: unknown unit "' + unit + '"');
        }
    }

    function startOf(time, unit, locale, ordinal) {
        var d = new Date(time);
        switch (unit) {
            case 'millisecond': return +d;
            case 'second':  d.setMilliseconds(0); break;
            case 'minute':  d.setSeconds(0, 0); break;
            case 'hour':    d.setMinutes(0, 0, 0); break;
            case 'day':     d.setHours(0, 0, 0, 0); break;
            case 'week':
            case 'isoWeek': {
                d.setHours(0, 0, 0, 0);
                // ISO weeks start on Monday; a numeric ordinal (0-6) shifts the
                // start day within the week, anything else (e.g. true) stays Monday.
                var shift = typeof ordinal === 'number'
                    ? Math.min(Math.max(Math.trunc(ordinal), 0), 6)
                    : 0;
                var sinceMonday = (d.getDay() + 6) % 7;
                d.setDate(d.getDate() - sinceMonday + shift);
                break;
            }
            case 'month':   d.setDate(1); d.setHours(0, 0, 0, 0); break;
            case 'quarter': d.setMonth(Math.floor(d.getMonth() / 3) * 3, 1);
                            d.setHours(0, 0, 0, 0); break;
            case 'year':    d.setMonth(0, 1); d.setHours(0, 0, 0, 0); break;
            default: throw new Error('chart-datetime-adapter: unknown unit "' + unit + '"');
        }
        return +d;
    }

    function endOf(time, unit) {
        switch (unit) {
            case 'millisecond': return time;
            case 'second':      return startOf(time, 'second') + 1000 - 1;
            case 'minute':      return startOf(time, 'minute') + 60000 - 1;
            case 'hour':        return startOf(time, 'hour') + 3600000 - 1;
            case 'day':         return startOf(time, 'day') + 86400000 - 1;
            case 'week':
            case 'isoWeek':     return startOf(time, unit) + 604800000 - 1;
            default:            return add(startOf(time, unit), 1, unit) - 1;
        }
    }

    // Register with Chart.js 4 - the same hook chartjs-adapter-moment uses:
    // its methods are copied onto the base adapter's prototype.
    Chart._adapters._date.override({
        _id: 'native',
        formats: function () {
            return {
                datetime: 'DD.MM.YY HH:mm',
                millisecond: 'HH:mm:ss.SSS',
                second: 'HH:mm:ss',
                minute: 'HH:mm',
                hour: 'HH',
                day: 'DD.MM.YY',
                week: 'DD.MM.YY',
                month: 'MM.YY',
                quarter: 'YYYY',
                year: 'YYYY'
            };
        },
        parse: parse,
        format: format,
        add: add,
        diff: diff,
        startOf: startOf,
        endOf: endOf
    });
})();
