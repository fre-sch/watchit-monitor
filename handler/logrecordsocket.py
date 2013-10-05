import logging
import tornado.websocket
from uuid import uuid4


def uuid():
    return str(uuid4())


logger = logging.getLogger(__name__)


class LogRecordSocket(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(LogRecordSocket, self).__init__(
            application, request, **kwargs)
        self.amqp_client = application.amqp_client
        self.amqp_channel = None
        self.socket_id = uuid()
        self.consumer_tag = "mon.websocket.{}".format(self.socket_id)
        self.queue_name = self.consumer_tag

    def open(self):
        logger.info('websocket open %s', self.socket_id)
        self.amqp_client.open_channel(self.start_amqp_consumer)

    def on_close(self):
        logger.info("websocket closed %s", self.socket_id)
        self.stop_amqp_consumer()

    def stop_amqp_consumer(self):
        self.amqp_channel.basic_cancel(
            self.on_cancel, self.consumer_tag)

    def start_amqp_consumer(self, channel):
        logger.info("amqp channel open")
        self.amqp_channel = channel
        self.amqp_channel.queue_declare(
            self.on_queue_declareok,
            self.queue_name,
            durable=False,
            auto_delete=True
        )

    def on_cancel(self, method):
        self.amqp_channel.close()

    def on_queue_declareok(self, method):
        logger.info('queue declared')
        self.amqp_channel.queue_bind(
            self.on_queue_bindok,
            self.queue_name,
            self.settings["LogRecordSocket"]["exchange"],
            self.settings["LogRecordSocket"]["routing_key"]
        )

    def on_queue_bindok(self, method):
        logger.info('queue bound, start consuming')
        self.amqp_channel.basic_consume(
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
