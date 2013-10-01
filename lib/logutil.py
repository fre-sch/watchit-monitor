from contextlib import contextmanager
from datetime import datetime
import logging
import ujson


amqp_logger = logging.getLogger('amqp')


class ExcludeFilter(logging.Filter):
    def filter(self, record):
        return not record.name.startswith(self.name)


class JsonFormatter(logging.Formatter):
    def format(self, record):
        try:
            record_data = vars(record)
            record_data.pop("exc_info")
            record_data["created"] = \
                datetime.fromtimestamp(record_data["created"]).isoformat()
            return ujson.dumps(record_data)
        except:
            amqp_logger.debug("ujson.dumps error: %s", vars(record))
            return "{'error': 'ujson.dumps error'}"


class AmqpHandler(logging.Handler):
    def __init__(self, amqp_client):
        super(AmqpHandler, self).__init__()
        self.amqp_client = amqp_client
        self.setFormatter(JsonFormatter())
        self.addFilter(ExcludeFilter('amqp'))
        self.addFilter(ExcludeFilter('pika'))

    def emit(self, record):
        message = self.format(record)
        amqp_logger.debug('publish %s', message)
        self.amqp_client.publish(
            'amq.topic',
            "logging.%s" % record.levelname,
            message,
            content_type="application/json"
        )


class ContextFilter(logging.Filter):
    def __init__(self, context):
        self.context = context

    def filter(self, record):
        try:
            record.context.update(self.context)
        except AttributeError:
            record.context = self.context
        return True


@contextmanager
def context(**kwargs):
    root_logger = logging.getLogger()
    context_filter = ContextFilter(kwargs)
    for handler in root_logger.handlers:
        handler.addFilter(context_filter)
    yield
    for handler in root_logger.handlers:
        handler.removeFilter(context_filter)
