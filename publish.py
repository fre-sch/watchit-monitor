#!/usr/bin/env python
import logging

import config
from lib.amqp import BlockingClient
from lib import logutil


def logging_config():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger('pika').setLevel(logging.WARNING)

    amqp_client = BlockingClient(config.amqp["url"])
    amqp_handler = logutil.AmqpHandler(amqp_client)

    root_logger = logging.getLogger()
    root_logger.addHandler(amqp_handler)


if __name__ == "__main__":
    logging_config()
    logger = logging.getLogger("wsgi.checkoutapi")

    with logutil.context(
            customer_id=45,
            order_id=123):
        logger.debug('request order create')

        logger = logging.getLogger("consumer.merchantapi.orderreceive")
        with logutil.context(merchant_id=1):
            logger.info('order created')

        with logutil.context(merchant_id=2):
            logger.info('order created')

        with logutil.context(merchant_id=3):
            try:
                raise Exception("merchant not reached")
            except:
                logger.exception("merchant not reached")

        logger = logging.getLogger("collin.libs.mail")
        logger.info('mail send')

