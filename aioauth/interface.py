import asyncio
import aio_pika
from .utils import current_loop


async def set_connection():
    conn = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/", loop=current_loop)
    ch = await connection.channel()
    inbound_q = await channel.declare_queue("inbound", auto_delete=True)
    outbound_q = await channel.declare_queue("outbound", auto_delete=True)
    return conn, ch, inbound_q, outbound_q


connection, channel, inbound_queue, outbound_queue = asyncio.run(set_connection())


class AuthMS:
    async def make_request(self, type: str, data: dict, timeout=10):
        async with inbound_queue.iterator() as inbound_queue_iter:
            async for message in inbound_queue_iter:
                async with message.process():
                    print(message.body)
                    if inbound_queue.name in message.body.decode():
                        break
