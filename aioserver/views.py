from aioelasticsearch import Elasticsearch
from aioelasticsearch.helpers import Scan

from .utils import json_response
from ..aioauth.interface import AuthMS
from ..crawler.interface import CrawlerMS

auth_ms = AuthMS()
crawler_ms = CrawlerMS()


async def singup(request):
    data = await request.json()
    return await json_response(await auth_ms.make_request(request_type='singup', data=data, timeout=5))


async def login(request):
    data = await request.json()
    return await json_response(await auth_ms.make_request(request_type='login', data=data, timeout=5))


async def current_user(request):
    data = {'token': request.headers.get('authorization').split(' ')[1]}
    return await json_response(await auth_ms.make_request('validate', data=data, timeout=5))


async def index(request):
    data = await request.json()
    data.update({'email': request['user']['email']})
    return await json_response(await crawler_ms.make_nowait_request('index', data))
