import asyncio
import datetime
import pickle
import uuid
import aio_pika
from project_config import crawler_queue_name
from crawler.utils import current_loop, set_connection
from crawler.settings import TIME_REFRESH_MINUTES
from async_orm.models import CrawlerStats, User
from async_orm.exceptions import DoesNotExist

connection, channel, queue = current_loop.run_until_complete(set_connection(current_loop))


class CrawlerMS:
    async def make_nowait_request(self, request_type: str, data: dict):
        try:
            request_id = uuid.uuid1()
            message_body = pickle.dumps({'request_id': request_id.hex, 'type': request_type, 'data': data})

            author = await User.objects.get(email=data['email'])
            try:
                cs = await CrawlerStats.objects.get(domain=data['domain'])
                if cs.time + datetime.timedelta(minutes=TIME_REFRESH_MINUTES) < datetime.datetime.now():
                    cs.author_id = author.id
                    cs.time = datetime.datetime.now()
                    await cs.save()
                else:
                    wait_time = (cs.time + datetime.timedelta(
                        minutes=TIME_REFRESH_MINUTES) - datetime.datetime.now()).total_seconds() / 60
                    return {'status': 'bad_request',
                            'error_text': 'You need to wait {:0.1f} minutes for update index'.format(wait_time)}
            except DoesNotExist:
                cs = await CrawlerStats.objects.create(domain=data['domain'], author_id=author.id,
                                                       https=data['https'],
                                                       time=datetime.datetime.now())

            await channel.default_exchange.publish(
                aio_pika.Message(body=message_body),
                routing_key=crawler_queue_name)

            return {'status': 'ok', 'data': {'id': cs.id, 'domain': cs.domain, 'https': cs.https, 'time': str(cs.time)}}
        except (ValueError, KeyError):
            return {'status': 'error', 'error_text': 'Wrong credentials were given to crawler'}
