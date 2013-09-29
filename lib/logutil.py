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
            'collins.logging', "logging", message,
            content_type="application/json")
