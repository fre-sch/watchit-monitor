

$(function() {
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
        },
        setVisible: function(visible){
            this.set({"visible": visible});
            logRecordStore.each(function(element){
                if(element.get('name') == this.get('name')){
                    element.set({"visible": visible});
                    console.log(element, element.get("visible"));
                }
            }, this);
        }
    });
    var LogRecordView = Backbone.View.extend({
        template: _.template($("#log-record-tpl").html()),
        render: function(){
            this.$el.html(this.template(this.model.toJSON()));
            this.$el.toggle(this.model.get("visible"));
            this.$el.find('time').timeago();
            return this;
        },
        initialize: function(){
           this.listenTo(this.model, 'change:visible', function(){
               this.$el.slideToggle();
           }, this); 
        }
    });
    var LogChannelView = Backbone.View.extend({
        template: _.template($("#log-channel-tpl").html()),
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
            this.$el.find('.glyphicon').toggleClass('glyphicon-ok-sign').toggleClass('glyphicon-remove-sign');
            this.model.setVisible(!visible);
        }
    });
    var LogRecordCollection = Backbone.Collection.extend({model: LogRecord});
    var LogChannelCollection = Backbone.Collection.extend({model: LogChannel});
    
    // instances
    var logRecordStore = new LogRecordCollection;
    var logChannelStore = new LogChannelCollection;
    
    var service = new Service('ws://localhost:8888/ws');


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
        logRecordStore.add(logRecord);
    });

    service.connect();

    $("body").on("click", ".logrecord .panel-heading", function() {
        $(this).next().slideToggle();
    });

});
