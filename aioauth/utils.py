import asyncio
import aio_pika
import bcrypt
from settings import rabbit_connection, inbound_name, outbound_name
from settings import set_logger

current_loop = asyncio.get_event_loop()
aioauth_logger = set_logger('aioauth')


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


async def set_connection(loop):
    conn = await aio_pika.connect_robust(rabbit_connection, loop=loop)
    ch = await conn.channel()
    await ch.set_qos(prefetch_count=1)

    inbound_q = await ch.declare_queue(inbound_name)
    outbound_q = await ch.declare_queue(outbound_name)

    outbound_exchange = await ch.declare_exchange('outbound_exchange', aio_pika.ExchangeType.FANOUT)
    await outbound_q.bind(outbound_exchange)

    return conn, ch, inbound_q, outbound_q
