from os.path import realpath, dirname
from os.path import join as pathjoin


base_path = realpath(pathjoin(dirname(__file__), '..'))

amqp = dict(
    url="amqp://guest:guest@server:5672/%2F",
)

tornado = dict(
    static_path=pathjoin(base_path, 'static'),
    debug=True,
    amqp_client=amqp,
    LogRecordSocket=dict(
        exchange="amq.topic",
        routing_key="logging.*",
    )
)

log = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(levelname)s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        '': {
            'level': "DEBUG",
            'handlers': ['console'],
            'propagate': True,
        },
        'pika': {'level': 'WARNING'},
    },
}
