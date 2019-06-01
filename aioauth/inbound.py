import asyncio
import pickle
import aio_pika

from project_config import rabbit_connection
from aioauth.utils import inbound_name, outbound_name
from aioauth.tasks import LoginTask, SignupTask, ValidateTask


async def main(loop):
    connection = await aio_pika.connect_robust(rabbit_connection, loop=loop)
    methods_dict = {'login': LoginTask, 'signup': SignupTask, 'validate': ValidateTask}

    async with connection:
        channel = await connection.channel()
        inbound_queue = await channel.declare_queue(inbound_name)

        async with inbound_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = pickle.loads(message.body)

                    if body['type'] in methods_dict:
                        r = await methods_dict[body['type']](**body['data']).perform()
                        message_body = pickle.dumps({
                            'request_id': body['request_id'],
                            'type': body['type'],
                            'data': r
                        })

                        await channel.default_exchange.publish(
                            aio_pika.Message(body=message_body),
                            routing_key=outbound_name)
                    else:
                        message_body = pickle.dumps({
                            'request_id': body['request_id'],
                            'type': body['type'],
                            'data': {
                                'status': 'error',
                                'error_text': 'Wrong type'
                            }
                        })

                        await channel.default_exchange.publish(
                            aio_pika.Message(body=message_body),
                            routing_key=outbound_name)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print('[*] Waiting auth messages!')
    loop.run_until_complete(main(loop))
    loop.close()
