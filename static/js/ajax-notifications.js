var WSMessageUrl = 'ws/ui'; // eslint-disable-line xo/filename-case
var test = !1;

var iconUrl = 'images/ico/favicon-120.png';

PNotify.prototype.options.addclass = 'stack-bottomright';
PNotify.prototype.options.buttons.closer_hover = !1; // eslint-disable-line camelcase
PNotify.prototype.options.delay = 5000;
PNotify.prototype.options.desktop = {desktop: !0, icon: iconUrl};
PNotify.prototype.options.hide = !0;
PNotify.prototype.options.history = !1;
PNotify.prototype.options.shadow = !1;
PNotify.prototype.options.stack = {dir1: 'up', dir2: 'left', firstpos1: 25, firstpos2: 25};
PNotify.prototype.options.styling = 'jqueryui';
PNotify.prototype.options.width = '340px';
PNotify.desktop.permission();

function displayPNotify(type, title, message) {
    new PNotify({ // eslint-disable-line no-new
        type: type,
        title: title,
        text: message.replace(/<br[\s\/]*(?:\s[^>]*)?>/ig, '\n')
            .replace(/<[\/]?b(?:\s[^>]*)?>/ig, '*')
            .replace(/<i(?:\s[^>]*)?>/ig, '[').replace(/<[\/]i>/ig, ']')
            .replace(/<(?:[\/]?ul|\/li)(?:\s[^>]*)?>/ig, '').replace(/<li(?:\s[^>]*)?>/ig, '\n* ')
    });
}

function WSCheckNotifications() {
    var ws = new WebSocket("ws://" + window.location.hostname + ":" + window.location.port + WSMessageUrl);
    ws.onmessage = function (evt) {
        var parsedJson = $.parseJSON(evt.data);

        // Add handling for different kinds of events. For ex: {"event": "notification", "data": {"title": ..}}
        if (parsedJson.event === 'notification') {
            displayPNotify(parsedJson.data.type, parsedJson.data.title, parsedJson.data.body);
        }
    };
}

$(document).ready(function() {
    WSCheckNotifications();
    if (test) {
        displayPNotify('notice', 'test', 'test<br><i class="test-class">hello <b>world</b></i><ul><li>item 1</li><li>item 2</li></ul>');
    }
});
