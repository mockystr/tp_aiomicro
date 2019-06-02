import json
import bcrypt
from aiohttp import web
from urllib.parse import urlparse
from aioauth.interface import AuthMS
from crawler.interface import CrawlerMS
from aioelasticsearch import Elasticsearch

auth_ms = AuthMS()
crawler_ms = CrawlerMS()
es = Elasticsearch()

dsn = "dbname={} user={} password={} host= {}".format('asynctest',
                                                      'emirnavruzov',
                                                      'qwe123',
                                                      '127.0.0.1')


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
