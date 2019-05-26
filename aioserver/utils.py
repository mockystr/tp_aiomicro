import datetime
import json
import jwt
from aiohttp import web
from .settings import sharable_secret
from .exceptions import ExpiredToken


async def json_response(data):
    return web.Response(text=json.dumps(data), headers={'content-type': 'application/json'})




dsn = "dbname={} user={} password={} host= {}".format('asynctest',
                                                      'emirnavruzov',
                                                      'qwe123',
                                                      '127.0.0.1')
