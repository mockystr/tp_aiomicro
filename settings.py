import logging

from os import getenv

TOKEN_EXPIRE_MINUTES = 30
TIME_REFRESH_MINUTES = 0.1
RPS = 100

rabbit_connection = f"amqp://guest:guest@" \
    f"{getenv('HOST_RABBITMQ', 'localhost')}/"
inbound_name, outbound_name = "inbound", "outbound"
crawler_queue_name = "crawler_inbound"

sharable_secret = 'iJDJJlX2RhdGUiiJDqqmQ5vV1QiLTmV6WlPvyz-uF5MCJ9.7WpQEyJD'


def set_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)-8s [%(name)s.%(filename)s:%(lineno)s '
        '%(funcName)s]  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger
