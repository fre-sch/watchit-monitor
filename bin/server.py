#!/usr/bin/env python
import logging
import logging.config
from handler import LogRecordSocket
import config
from lib.amqp import TornadoClient
from tornado.web import (
    URLSpec,
    Application,
    RedirectHandler,
    StaticFileHandler,
)
from tornado.ioloop import IOLoop


logging.config.dictConfig(config.log)
logger = logging.getLogger('application')
handlers = [
    URLSpec(r"/logrecordsocket", LogRecordSocket, name="logrecordsocket"),
    URLSpec(r"/", RedirectHandler, {"url": "/index.html"}),
    URLSpec(r"/(.*)", StaticFileHandler, dict(
        path=config.tornado.pop('static_path')
    ), name='static'),
]
application = Application(handlers, **config.tornado)
application.amqp_client = TornadoClient(config.tornado["amqp_client"]["url"])


if __name__ == "__main__":
    application.listen(8888, address='0.0.0.0')
    ioloop = IOLoop.instance()
    ioloop.add_timeout(500, application.amqp_client.connect)
    try:
        ioloop.start()
    except KeyboardInterrupt:
        ioloop.stop()
