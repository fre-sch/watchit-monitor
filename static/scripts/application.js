"use strict";

$(function() {
    // models
    var LogRecord = Backbone.Model.extend({
        defaults: {
            visible: true
        }
    });
    var LogChannel = Backbone.Model.extend({
        defaults: {
            numLogRecords: 0,
            visible: true
        },
        setVisible: function(visible){
            this.set({"visible": visible});
            logRecordStore.each(function(element){
                if(element.get('name') == this.get('name')){
                    element.set({"visible": visible});
                }
            }, this);
        },
        initialize: function() {
            this.listenTo(logRecordStore, "add", function(logRecord) {
                if (logRecord.get("name") == this.get("name"))
                    this.set({"numLogRecords": this.get("numLogRecords") + 1});
            });
        }
    });

    // views
    var LogRecordView = Backbone.View.extend({
        className: "log-record",
        template: _.template($("#log-record-tpl").html(), false, {"variable": "data"}),
        render: function(){
            this.$el.html(this.template(this.model.toJSON()));
            this.$el.toggle(this.model.get("visible"));
            this.$el.find(".log-record-body").hide();
            var levelnameClass = {
                INFO: "",
                WARNING: "alert-warning",
                ERROR:"alert-danger",
                CRITICAL: "alert-danger",
                FATAL: "alert-danger"
            }[this.model.get("levelname")];
            if (levelnameClass)
                this.$el.find(".log-record-head").addClass(levelnameClass);
            return this;
        },
        initialize: function(){
           this.listenTo(this.model, 'change:visible', function(){
               this.$el.toggle();
           }, this);
        }
    });
    var LogChannelView = Backbone.View.extend({
        template: _.template($("#log-channel-tpl").html(), false, {"variable": "data"}),
        tagName: 'a',
        className: "list-group-item",
        initialize: function(){
            this.listenTo(this.model, 'change:numLogRecords', function(model){
                this.$el.find('span.badge').text(model.get('numLogRecords'));
            }, this);
        },
        render: function(){
            this.$el.html(this.template(this.model.toJSON()));
            return this;
        },
        events: {
            "click": "toggleVisibility"
        },
        toggleVisibility: function(){
            var visible = this.model.get('visible');
            this.$el.find('.glyphicon')
                .toggleClass('glyphicon-ok-sign')
                .toggleClass('glyphicon-remove-sign');
            this.model.setVisible(!visible);
        }
    });
    var ConnectionView = Backbone.View.extend({
        el: "#connection",
        setStatus: function(status) {
            var $status_badge = this.$el.find("span.badge");
            $status_badge.text(status);
        }
    });

    // collections
    var LogRecordCollection = Backbone.Collection.extend({
        model: LogRecord,
    });
    var LogChannelCollection = Backbone.Collection.extend({model: LogChannel});

    // instances
    var connectionView = new ConnectionView;
    var logRecordStore = new LogRecordCollection;
    var logChannelStore = new LogChannelCollection;

    var service = new Service('ws://localhost:8888/logrecordsocket');
    // $(service).on("socket-connect", function() {
    //     console.info("socket-connect");
    //     connectionView.setStatus('connected');
    // });
    // $(service).on("socket-close", function() {
    //     console.info("socket-close");
    //     connectionView.setStatus('closed');
    // });
    // $(service).on("socket-error", function() {
    //     console.info("socket-error");
    //     connectionView.setStatus('error');
    // });


    logRecordStore.on('add', function(logRecord, collection, event){
        var view = new LogRecordView({model: logRecord});
        $("#log-records").append(view.render().el);

    });
    logChannelStore.on('add', function(logChannel, collection, event){
        var view = new LogChannelView({model: logChannel});
        $("#log-channels").append(view.render().el);
    });

    // create logrecord view and add to document
    $(service).on('logrecord', function(evt, record) {
        var logChannel = logChannelStore.findWhere({name: record.name});
        if (!logChannel) {
            logChannel = new LogChannel({"name": record.name});
            logChannelStore.add(logChannel);
        }

        var logRecord = new LogRecord(record);
        logRecord.set({visible: logChannel.get("visible")});
        logRecordStore.add(logRecord);
    });

    service.connect();

    $("body").on("click", ".log-record .log-record-head", function() {
        $(this).next().toggle();
    });

});
