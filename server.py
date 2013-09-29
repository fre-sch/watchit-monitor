#!/usr/bin/env python
import logging
import logging.config
from handler import NotifyWebSocketHandler
import config
from lib.amqp import TornadoClient
import tornado.ioloop
import tornado.web
from tornado.web import URLSpec


logging.config.dictConfig(config.log)
logger = logging.getLogger('application')
handlers = [
    URLSpec(r"/ws", NotifyWebSocketHandler, name="wshandler"),
    URLSpec(r"/(.*)", tornado.web.StaticFileHandler, dict(
        path=config.tornado.pop('static_path')
    ), name='static'),
]
application = tornado.web.Application(handlers, **config.tornado)
application.amqp_client = TornadoClient(config.amqp["url"])


if __name__ == "__main__":
    application.listen(8888, address='0.0.0.0')
    ioloop = tornado.ioloop.IOLoop.instance()
    ioloop.add_timeout(500, application.amqp_client.connect)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        ioloop.stop()
