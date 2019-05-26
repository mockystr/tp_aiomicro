import bcrypt
import json
from urllib.parse import urlparse
from aiohttp import web


async def json_response(data):
    return web.Response(text=json.dumps(data), headers={'content-type': 'application/json'})


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


async def get_domain(url):
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))


dsn = "dbname={} user={} password={} host= {}".format('asynctest',
                                                      'emirnavruzov',
                                                      'qwe123',
                                                      '127.0.0.1')
