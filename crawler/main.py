import asyncio
import pickle
from aio_pika import connect, IncomingMessage
from project_config import rabbit_connection, crawler_queue_name
from crawler.settings import RPS
from crawler.crawler import Crawler
from crawler.utils import collect_url, current_loop, set_connection
from async_orm.models import CrawlerStats


async def index_consumer(message: IncomingMessage):
    async with message.process():
        body = pickle.loads(message.body)
        url = await collect_url(body['data']['https'], body['data']['domain'])
        r = await Crawler(start_url=url, rps=RPS, max_count=50, loop=current_loop).main()

        if r is None:
            print('ERROR')
            return

        cs = await CrawlerStats.objects.get(domain=body['data']['domain'])
        cs.pages_count = r['pages']
        cs.avg_time_per_page = r['avg_time_per_page']
        cs.max_time_per_page = r['max_time_per_page']
        cs.min_time_per_page = r['min_time_per_page']
        await cs.save()


async def main(loop):
    connection, channel, queue = await set_connection(loop)

    await queue.consume(index_consumer, no_ack=False)


if __name__ == "__main__":
    main_loop = asyncio.get_event_loop()
    main_loop.create_task(main(main_loop))
    print("[*] Waiting for crawler messages. To exit press CTRL+C")
    main_loop.run_forever()
