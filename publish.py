#!/usr/bin/env python
import logging

import config
from lib.amqp import BlockingClient
from lib.logutil import AmqpHandler


def logging_config():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger('pika').setLevel(logging.WARNING)

    amqp_client = BlockingClient(config.amqp["url"])
    amqp_handler = AmqpHandler(amqp_client)

    root_logger = logging.getLogger()
    root_logger.addHandler(amqp_handler)


if __name__ == "__main__":
    logging_config()
    logger = logging.getLogger("foo.bar")
    logger.info('test')
    try:
        raise Exception('dummy')
    except:
        logger.exception("dummy test")

    import time
    for i in range(0, 100):
        time.sleep(2)
        logger.info("message blaster [%s]", i)
