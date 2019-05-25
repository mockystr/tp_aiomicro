from aiohttp import web
from utils import dsn, json_response
from pprint import pprint
from aioelasticsearch import Elasticsearch
from settings import index_name
from aioelasticsearch.helpers import Scan
from async_orm.models import User
import datetime


async def singup(request):
    try:
        await User.objects.create(email=request.query['email'], password=request.query['password'],
                                  name=request.query.get('name'), created_date=datetime.datetime.now())
        return await json_response({'status': 'ok', 'data': {}})
    except KeyError:
        return await json_response({'status': 'error', 'error_text': 'You must write email and password'})
    except:
        return await json_response({'status': 'error', 'error_text': 'Something went wrong'})


async def index(request):
    r = {'status': 'success', 'text': 'Hello, im index handler'}
    return await json_response(r)


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
