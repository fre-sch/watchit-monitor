// definitions
var LogRecord = Backbone.Model.extend({
    defaults: {
        visible: true
    }
});
var LogChannel = Backbone.Model.extend({
    defaults: {
        numLogRecords: 0,
        visible: true
    }
});
var LogRecordView = Backbone.View.extend({
    template: _.template($("#logrecord-tpl").text())
});
var LogRecordCollection = Backbone.Collection.extend({model: LogRecord});
var LogChannelCollection = Backbone.Collection.extend({model: LogChannel});

// instances
var logRecordStore = new LogRecordCollection;
var logChannelStore = new LogChannelCollection;

var service = new Service('ws://localhost:8888/ws');

$(function() {

    // create logrecord view and add to document
    $(service).on('logrecord', function(evt, record) {
        console.info("service.logrecord", record);
        var logChannel = logChannelStore.findWhere({name: record.name});
        if (!logChannel) {
            logChannel = new LogChannel({"name": record.name});
            logChannelStore.add(logChannel);
            logChannel.listenTo(logRecordStore, "add", function(logRecord) {
                if (logRecord.get("name") == this.get("name"))
                    this.set({"numLogRecords": this.get("numLogRecords") + 1});
            });
        }

        var logRecord = new LogRecord(record);
        logRecord.set({visible: logChannel.get("visible")});
        logRecord.listenTo(logChannel, "change:visible", function(logChannel, visible) {
            this.set({"visible": visible});
        });
        logRecordStore.add(logRecord);
    });

    // service.connect();

    $("body").on("click", ".logrecord .panel-heading", function() {
        $(this).next().slideToggle();
    });

});
