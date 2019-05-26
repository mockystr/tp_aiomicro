import bcrypt
import datetime
import json
import jwt
from aiohttp import web
from .settings import sharable_secret
from .exceptions import ExpiredToken


async def json_response(data):
    return web.Response(text=json.dumps(data), headers={'content-type': 'application/json'})


def get_hashed_password(plain_text_password):
    return bcrypt.hashpw(plain_text_password, bcrypt.gensalt())


def check_password(plain_text_password, hashed_password):
    return bcrypt.checkpw(plain_text_password, hashed_password)


dsn = "dbname={} user={} password={} host= {}".format('asynctest',
                                                      'emirnavruzov',
                                                      'qwe123',
                                                      '127.0.0.1')
