from aioelasticsearch import Elasticsearch
from aioelasticsearch.helpers import Scan

from .utils import json_response
from ..aioauth.interface import AuthMS
from ..crawler.interface import CrawlerMS
from ..async_orm.models import CrawlerStats, User, Token

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
    data = {'token': request.headers.get('authorization').split(' ')[1]}
    validate_response = await auth_ms.make_request('validate', data=data, timeout=5)
    if validate_response['status'] != 'ok':
        return await json_response(validate_response)

    data = await request.json()
    data.update({'email': request['user']['email']})
    print('from views data', data)
    return await json_response(await crawler_ms.make_nowait_request('index', data))


async def stat(request):
    data = {'token': request.headers.get('authorization').split(' ')[1]}
    validate_response = await auth_ms.make_request('validate', data=data, timeout=5)
    if validate_response['status'] != 'ok':
        return await json_response(validate_response)

    author = await User.objects.get(email=request['user']['email'])
    cs = await CrawlerStats.objects.filter(author_id=author.id)
    return await json_response({'status': 'ok', 'data': [await i.to_dict() async for i in cs]})
    # except Exception as e:
    #     return await json_response({'status': 'error', 'error_text': str(e)})


async def search(request):
    pass