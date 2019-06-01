from aioelasticsearch import Elasticsearch
from aioelasticsearch.helpers import Scan

from aioserver.utils import json_response, get_domain
from aioauth.interface import AuthMS
from crawler.interface import CrawlerMS
from async_orm.models import CrawlerStats, User

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
    es = Elasticsearch()
    try:
        q = request.query['q']
        limit = int(request.query.get('limit', 0))
        offset = int(request.query.get('offset', 0))

        if limit > 100:
            raise
    except Exception:
        return await json_response({'status': 'bad_request', 'error_text': 'Wrong parameters'})

    body = {'query': {'match': {'text': q}}}

    all_documents = ['{}://{}'.format('https' if i.https else 'http', i.domain) async for i in
                     await CrawlerStats.objects.all()]
    index_names_docs = [''.join([i for i in ii
                                 if i not in ('[', '"', '*', '\\\\', '\\', '<', '|', ',', '>', '/', '?', ':')]) for ii
                        in all_documents]

    response_data = {'total_hits': 0, 'count': 0, 'documents_in_list': [], 'results': []}

    for i, index_name in enumerate(index_names_docs):
        async with Scan(es,
                        index=index_name,
                        doc_type='crawler',
                        query=body, ) as scan_res:
            res_source = [{'id': i['_id'], **i['_source']} async for i in scan_res]
            response_data['total_hits'] += len(res_source)
            response_data['results'].extend(res_source)

    count = len(response_data['results'])
    if limit:
        response_data['results'] = response_data['results'][offset: min(limit + offset, count)]
    else:
        response_data['results'] = response_data['results'][offset:]

    response_data['documents_in_list'] = list(set([await get_domain(i['url']) for i in response_data['results']]))
    response_data['count'] = len(response_data['results'])
    return await json_response({'status': 'ok', 'data': response_data})
