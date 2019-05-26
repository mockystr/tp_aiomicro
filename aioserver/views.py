import datetime
import jwt

from aioelasticsearch import Elasticsearch
from aioelasticsearch.helpers import Scan
from validate_email import validate_email

from ..async_orm.models import User, Token, CrawlerStats
from .utils import dsn, json_response, get_hashed_password, check_password
from .settings import index_name, sharable_secret, TOKEN_EXPIRE_MINUTES
from .exceptions import UserExists, ExpiredToken
from ..async_orm.exceptions import DoesNotExist
from ..aioauth.interface import AuthMS

auth_ms = AuthMS()


async def singup(request):
    data = await request.json()
    return await json_response(await auth_ms.make_request(request_type='singup', data=data, timeout=5))


async def login(request):
    data = await request.json()
    return await json_response(await auth_ms.make_request(request_type='login', data=data, timeout=5))


async def current_user(request):
    data = {'email': request['user']['email'], 'token': request.headers.get('authorization').split(' ')[1]}
    return await json_response(await auth_ms.make_request('validate', data=data, timeout=5))


async def search(request):
    es = Elasticsearch()

    q = request.query.get('q')
    try:
        limit = int(request.query.get('limit', 0))
        offset = int(request.query.get('offset', 0))
    except:
        return await json_response({'response': 'wrong query'})

    body = {}
    if q:
        body['query'] = {'match': {'text': q}}

    async with Scan(es,
                    index=index_name,
                    doc_type='crawler',
                    query=body, ) as scan_res:
        res_source, count = await format_search(scan_res, limit, offset)
        text = {'total_hits': count, 'count': len(res_source), 'results': res_source}
        return await json_response(text)


async def format_search(res, limit, offset):
    res_source = [{'id': i['_id'], **i['_source']} async for i in res]
    count = len(res_source)
    if limit:
        return res_source[offset: min(limit + offset, count)], count
    return res_source[offset:], count
