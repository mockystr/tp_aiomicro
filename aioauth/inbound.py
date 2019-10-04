import asyncio
import pickle
import aio_pika

from project_config import rabbit_connection
from aioauth.utils import inbound_name, outbound_name, aioauth_logger
from aioauth.tasks import LoginTask, SignupTask, ValidateTask


async def main(loop):
    connection = await aio_pika.connect_robust(rabbit_connection, loop=loop)
    methods_dict = {'login': LoginTask, 'signup': SignupTask, 'validate': ValidateTask}
    async with connection:
        channel = await connection.channel()
        inbound_queue = await channel.declare_queue(inbound_name)
        outbound_exchange = await channel.declare_exchange('outbound_exchange', aio_pika.ExchangeType.FANOUT)

        async with inbound_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = pickle.loads(message.body)

                    aioauth_logger.info(body)

                    try:
                        r = await methods_dict[body['type']](**body['data']).perform()
                        message_body = pickle.dumps({
                            'request_id': body['request_id'],
                            'type': body['type'],
                            'data': r
                        })
                    except Exception as e:
                        message_body = pickle.dumps({
                            'request_id': body['request_id'],
                            'type': body['type'],
                            'data': {
                                'status': 'error',
                                'reason': str(e)
                            }
                        })

                    await outbound_exchange.publish(
                        aio_pika.Message(body=message_body),
                        routing_key=outbound_name)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    aioauth_logger.info('[*] Waiting auth messages!')
    loop.run_until_complete(main(loop))
    loop.close()
