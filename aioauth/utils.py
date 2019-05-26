import asyncio
import aio_pika
import bcrypt

current_loop = asyncio.get_event_loop()
inbound_name, outbound_name = "inbound", "outbound"


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


async def set_connection(loop):
    conn = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/", loop=loop)
    ch = await conn.channel()
    inbound_q = await ch.declare_queue(inbound_name)
    outbound_q = await ch.declare_queue(outbound_name)
    return conn, ch, inbound_q, outbound_q