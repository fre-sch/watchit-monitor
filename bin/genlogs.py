#!/usr/bin/env python
import logging
import config
from lib.amqp import BlockingClient
from lib import logutil
import argparse
import random


parser = argparse.ArgumentParser(description="generate some log messages")
parser.add_argument(
    "-n", type=int, action='store', default=1,
    help="generate <n> log messages")
parser.add_argument(
    "-l", type=str.split, action="store", default=["root"],
    help="list of logger names (space separated)")
parser.add_argument(
    "-t", type=str.split, action="store", default=["info"],
    help="list of logging levels (space separated)")
parser.add_argument(
    "message", type=str, action="store", default="default message {i}",
    help="log message (available format var {i})")


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
    args = parser.parse_args()
    for i in range(args.n):
        logger = logging.getLogger(random.choice(args.l))
        level = random.choice(args.t)
        getattr(logger, level)(args.message.format(i=i))

