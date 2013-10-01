/*

Service connects via WebSocket.
Expects message to be JSON-RPC (v2).
Uses the jsonrpc.method name and triggers it as event, passing jsonrpc.params

*/

Service = function(url) {
    this.url = url;
    this.socket = null;
};

Service.prototype.connect = function() {
    var self = this;
    this.socket = new WebSocket(this.url);
    this.socket.onopen = function(evt) {
        $(self).trigger('socket-connect');
    };
    this.socket.onerror = function(evt) {
        $(self).trigger('socket-error');
    };
    this.socket.onclose = function(evt) {
        $(self).trigger('socket-close');
    };
    this.socket.onmessage = function(evt) {
        var rpc = JSON.parse(evt.data);
        $(self).trigger(rpc.method, rpc.params);
    };
};
