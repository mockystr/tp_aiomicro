from aioelasticsearch.helpers import Scan

from aioserver.utils import json_response, get_domain, auth_ms, crawler_ms, es
from async_orm.models import CrawlerStats
from aioserver.api_schemas import SearchViewSchema


async def signup(request):
    data = await request.json()
    return await json_response(await auth_ms.make_request(request_type='signup', data=data, timeout=5))


async def login(request):
    data = await request.json()
    return await json_response(await auth_ms.make_request(request_type='login', data=data, timeout=5))


async def current_user(request):
    return await json_response(await auth_ms.make_request('validate',
                                                          data={'token': request['user']['split_token']}, timeout=5))


async def index(request):
    data = await request.json()
    print(data.get('https'), data.get('domain'))
    if data.get('https') is None or data.get('domain') is None:
        return await json_response({'status': 'error', 'reason': 'Wrong data is given'}, status=400)

    data.update({'author_id': request['user']['user_id']})
    return await json_response(await crawler_ms.make_nowait_request('index', data))


async def stat(request):
    cs = await CrawlerStats.objects.filter(author_id=request['user']['user_id'])
    return await json_response({'status': 'ok', 'data': [await i.to_dict() async for i in cs]})


async def search(request):
    try:
        schema = SearchViewSchema()
        r = schema.dump({**request.query})
        print(schema.__dict__)
        print(r)
        q, limit, offset = r['q'], r['limit'], r['offset']
    except Exception as e:
        return await json_response({'status': 'bad_request', 'reason': str(e)})

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
