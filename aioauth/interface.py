import asyncio
import pickle
import uuid
import aio_pika
from .utils import current_loop, set_connection, inbound_name, outbound_name

connection, channel, inbound_queue, outbound_queue = current_loop.run_until_complete(set_connection(current_loop))


class AuthMS:
    async def make_request(self, request_type: str, data: dict, timeout=5):
        request_id = uuid.uuid1()
        await channel.default_exchange.publish(
            aio_pika.Message(body=pickle.dumps({'request_id': request_id.hex, 'type': request_type, 'data': data})),
            routing_key=inbound_name)

        queue = await channel.declare_queue(outbound_name)

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = pickle.loads(message.body)
                    print('from interface', body)
                    if request_id.hex == body['request_id']:
                        r = body['data']
                        break

        return r
