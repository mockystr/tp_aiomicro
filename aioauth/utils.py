import asyncio
import aio_pika

current_loop = asyncio.get_event_loop()
inbound_name, outbound_name = "inbound", "outbound"


async def set_connection(loop):
    conn = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/", loop=loop)
    ch = await conn.channel()
    inbound_q = await ch.declare_queue(inbound_name, auto_delete=True)
    outbound_q = await ch.declare_queue(outbound_name, auto_delete=True)
    return conn, ch, inbound_q, outbound_q
