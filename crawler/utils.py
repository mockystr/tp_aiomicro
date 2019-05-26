import asyncio
import aio_pika
import bcrypt

current_loop = asyncio.get_event_loop()
queue_name = "crawler_inbound"


async def set_connection(loop):
    conn = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/", loop=loop)
    ch = await conn.channel()
    await ch.set_qos(prefetch_count=1)
    q = await ch.declare_queue(queue_name)
    return conn, ch, q
