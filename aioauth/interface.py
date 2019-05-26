import asyncio
import aio_pika
from .utils import current_loop, set_connection, inbound_name, outbound_name

connection, channel, inbound_queue, outbound_queue = current_loop.run_until_complete(set_connection(current_loop))


class AuthMS:
    async def make_request(self, type: str, data: dict, timeout=10):
        await channel.default_exchange.publish(
            aio_pika.Message(
                body='Hello {}'.format(inbound_name).encode()
            ),
            routing_key=inbound_name
        )
