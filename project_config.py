from os import getenv

TOKEN_EXPIRE_MINUTES = 30
TIME_REFRESH_MINUTES = 0.1
RPS = 100

rabbit_connection = f"amqp://guest:guest@{getenv('HOST_RABBITMQ', 'localhost')}/"
inbound_name, outbound_name = "inbound", "outbound"
crawler_queue_name = "crawler_inbound"

sharable_secret = 'iJDJJlX2RhdGUiiJDqqmQ5vV1QiLTmV6WlPvyz-uF5MCJ9.7WpQEyJD'
