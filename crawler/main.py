import asyncio
import pickle
from aio_pika import connect, IncomingMessage
from .settings import RPS, START_URL
from .crawler import Crawler


async def crawler_consumer(message: IncomingMessage):
    body = pickle.dumps(message.body)
    print(body)
    print("Message body is: %r" % message.body)
    print("Before sleep!")
    await asyncio.sleep(5)  # Represents async I/O operations
    print("After sleep!")


async def main(loop):
    connection = await connect("amqp://guest:guest@localhost/", loop=loop)
    channel = await connection.channel()
    queue = await channel.declare_queue('crawler_inbound')

    await queue.consume(crawler_consumer, no_ack=True)


if __name__ == "__main__":
    main_loop = asyncio.get_event_loop()
    main_loop.create_task(main(main_loop))
    print("[*] Waiting for crawler messages. To exit press CTRL+C")
    main_loop.run_forever()

# if __name__ == '__main__':
#     # with pool ~14s
#     # best score was 11.5
#
#     # without pool ~50s
#     # sync 78s
#     asyncio.run(Crawler(start_url=START_URL, rps=RPS).main())
