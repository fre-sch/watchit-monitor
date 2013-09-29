import logging
import pika
from pika import adapters


logger = logging.getLogger("amqp")


class TornadoClient(object):

    def __init__(self, url):
        self.parameters = pika.URLParameters(url)
        self.connecting = False
        self.connection = None
        self.channel = None

    def connect(self):
        if self.connecting:
            logger.info('already connecting')
            return
        logger.info("connecting")
        self.connecting = True
        self.connection = adapters.TornadoConnection(
            self.parameters, on_open_callback=self.on_connection_open)
        self.connection.add_on_close_callback(self.on_connection_closed)

    def on_connection_open(self, connection):
        logger.info('connection opened')
        self.connection = connection
        self.connecting = False
        logger.info('opening channel')
        connection.channel(self.on_channel_open)

    def on_channel_open(self, channel):
        logger.info('channel opened')
        self.channel = channel

    def on_connection_closed(self, connection):
        logger.info("connection closed")


class BlockingClient(object):
    def __init__(self, url):
        self.parameters = pika.URLParameters(url)
        self._connection = None
        self._channel = None

    @property
    def connection(self):
        if self._connection is None:
            logger.info('open connection')
            self._connection = pika.BlockingConnection(self.parameters)
        return self._connection

    @property
    def channel(self):
        if self._channel is None:
            logger.info('open channel')
            self._channel = self.connection.channel()
        return self._channel

    def publish(self, ex, rk, msg, **kwargs):
        self.channel.basic_publish(ex, rk, msg, pika.BasicProperties(**kwargs))
