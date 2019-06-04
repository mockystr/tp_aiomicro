import asyncio
import aio_pika
from project_utils import set_logger
from project_config import rabbit_connection, crawler_queue_name
from aioelasticsearch import Elasticsearch

current_loop = asyncio.get_event_loop()
logger = set_logger('crawler')
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


async def set_connection(loop):
    conn = await aio_pika.connect_robust(rabbit_connection, loop=loop)
    ch = await conn.channel()
    await ch.set_qos(prefetch_count=1)
    q = await ch.declare_queue(crawler_queue_name)
    return conn, ch, q


async def collect_url(https, domain):
    return "{}://{}".format('https' if https == 1 else 'http', domain)
