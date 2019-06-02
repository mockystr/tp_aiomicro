import logging

TOKEN_EXPIRE_MINUTES = 30
TIME_REFRESH_MINUTES = 0.1
RPS = 100

rabbit_connection = "amqp://guest:guest@127.0.0.1/"
inbound_name, outbound_name = "inbound", "outbound"
crawler_queue_name = "crawler_inbound"

sharable_secret = 'iJDJJlX2RhdGUiiJDqqmQ5vV1QiLTmV6WlPvyz-uF5MCJ9.7WpQEyJD'
