import logging
import tornado.websocket


logger = logging.getLogger(__name__)


class NotifyWebSocketHandler(tornado.websocket.WebSocketHandler):
    def __init__(self, application, request, **kwargs):
        super(NotifyWebSocketHandler, self).__init__(
            application, request, **kwargs)
        self.consumer_tag = "monitor.collins.logging-{id}".format(
            id=id(self), remoteip=self.request.remote_ip,
        )
        self.queue_name = "monitor.collins.logging-{id}".format(
            id=id(self), remoteip=self.request.remote_ip,
        )

    def open(self):
        logger.info('websocket open %s', id(self))
        self.application.web_sockets.append(self)
        self.start_amqp_consumer()

    def on_close(self):
        logger.info("websocket closed %s", id(self))
        self.application.web_sockets.remove(self)
        self.stop_pika_consumer()

    def stop_pika_consumer(self):
        pika_client = self.application.pika_client
        pika_client.channel.basic_cancel(consumer_tag=self.consumer_tag)

    def start_amqp_consumer(self):
        amqp_client = self.application.amqp_client

        def queue_bindok(method):
            logger.info('queue bound')
            amqp_client.channel.basic_consume(
                self.on_pika_message,
                self.queue_name,
                exclusive=True,
                consumer_tag=self.consumer_tag,
                no_ack=True,
            )

        def queue_declareok(method):
            logger.info('queue declared')
            amqp_client.channel.queue_bind(
                queue_bindok, self.queue_name, 'collins.logging', '*')

        amqp_client.channel.queue_declare(
            queue_declareok, self.queue_name, durable=False, auto_delete=True)

    def on_pika_message(self, chan, meth, prop, body):
        self.write_message(body)
