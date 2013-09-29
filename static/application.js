function websocket_connect(reconnect) {
    if (reconnect > 5) {
        $("#status").addClass("alert-danger").text("abort after " + (reconnect - 1) + " tries.");
        return;
    }

    $("#status").text("connecting (" + reconnect + ")");

    var ws = new WebSocket("ws://localhost:8888/ws");

    ws.onopen = function() {
        $("#status").addClass("alert-success").text("connected");
    };

    ws.onerror = function() {
        console.log("websocket error", arguments);
        $("#status").addClass("alert-danger").text("error");
    };

    ws.onclose = function() {
        $("#status").addClass("alert-warning").text("closed, reconnecting");
        setTimeout(function() {
            websocket_connect(reconnect + 1)
        }, 2000);
    };

    ws.onmessage = function (evt) {
        record = JSON.parse(evt.data);
        logrecord_new(record);
    };
};

Templates = {};

function logrecord_new(record) {
    $(Templates.LogRecord(record))
        .hide()
        .prependTo("#logs")
        .slideDown()
        .find("time").timeago()
        ;
};

$(function() {
    websocket_connect(0);
    Templates.LogRecord = doT.template(
        $("#logrecord-tpl").text()
    );
    $("body").on("click", ".logrecord .panel-heading", function() {
        $(this).next().slideToggle();
    });
});
