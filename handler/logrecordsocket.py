import logging
import tornado.websocket


logger = logging.getLogger(__name__)


class LogRecordSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(LogRecordSocket, self).__init__(
            application, request, **kwargs)
        self.amqp_client = application.amqp_client
        self.consumer_tag = "monitor.collins.logging-{id}".format(
            id=id(self), remoteip=self.request.remote_ip,
        )
        self.queue_name = "monitor.collins.logging-{id}".format(
            id=id(self), remoteip=self.request.remote_ip,
        )

    def open(self):
        logger.info('websocket open %s', id(self))
        self.start_amqp_consumer()

    def on_close(self):
        logger.info("websocket closed %s", id(self))
        self.stop_amqp_consumer()

    def stop_amqp_consumer(self):
        self.amqp_client.channel.basic_cancel(consumer_tag=self.consumer_tag)

    def start_amqp_consumer(self):
        self.amqp_client.channel.queue_declare(
            self.queue_declareok,
            self.queue_name,
            durable=False,
            auto_delete=True
        )

    def queue_declareok(self, method):
        logger.info('queue declared')
        self.amqp_client.channel.queue_bind(
            self.queue_bindok,
            self.queue_name,
            self.settings["LogRecordSocket"]["exchange"],
            self.settings["LogRecordSocket"]["routing_key"]
        )

    def queue_bindok(self, method):
        logger.info('queue bound, start consuming')
        self.amqp_client.channel.basic_consume(
            self.on_amqp_message,
            self.queue_name,
            exclusive=True,
            consumer_tag=self.consumer_tag,
            no_ack=True,
        )

    def on_amqp_message(self, chan, meth, prop, body):
        response = u"""{{"jsonrpc":"2.0","method":"logrecord","params":{params},"id":{id}}}""".format(
            params=body, id=meth.delivery_tag)
        self.write_message(response)
