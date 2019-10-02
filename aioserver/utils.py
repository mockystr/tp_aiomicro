import json
import logging
import bcrypt
from aiohttp import web
from urllib.parse import urlparse
from aioauth.interface import AuthMS
from crawler.interface import CrawlerMS
from aioelasticsearch import Elasticsearch
from project_utils import set_logger

auth_ms = AuthMS()
crawler_ms = CrawlerMS()
es = Elasticsearch()
logger = set_logger('aioserver')

dsn = "dbname={} user={} password={} host= {}".format('asynctest',
                                                      'emirnavruzov',
                                                      'qwe123',
                                                      'db')


async def json_response(data, status=200):
    return web.Response(text=json.dumps(data),
                        headers={'content-type': 'application/json'},
                        status=status)


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


async def get_domain(url):
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))


async def get_post_data(request, schema):
    try:
        data = await request.json()
        logger.info(data)
        schema_obj = schema()
        schema_obj.load(data=data)
        return data
    except json.decoder.JSONDecodeError as e:
        logger.error(str(e))
        return {'status': 'error', 'reason': 'Expected data in request'}
    except Exception as e:
        return {'status': 'error', 'reason': str(e)}
