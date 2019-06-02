from aioelasticsearch.helpers import Scan
from aioserver.utils import logger
from aioserver.utils import json_response, get_domain, auth_ms, crawler_ms, es
from async_orm.models import CrawlerStats
from aioserver.api_schemas import SearchViewSchema


async def signup(request):
    data = await request.json()
    logger.info(data)
    r = await auth_ms.make_request(request_type='signup', data=data, timeout=5)
    logger.error(r) if r['status'] != 'ok' else logger.info(r)
    return await json_response(r, status=200 if r['status'] == 'ok' else 400)


async def login(request):
    data = await request.json()
    logger.info(data)
    r = await auth_ms.make_request(request_type='login', data=data, timeout=5)
    logger.error(r) if r['status'] != 'ok' else logger.info(r)
    return await json_response(r, status=200 if r['status'] == 'ok' else 400)


async def current_user(request):
    logger.info(request['user']['email'])
    r = await auth_ms.make_request('validate', data={'token': request['user']['split_token']}, timeout=5)
    logger.error(r) if r['status'] != 'ok' else logger.info(r)
    return await json_response(r, status=200 if r['status'] == 'ok' else 400)


async def index(request):
    data = await request.json()
    logger.info(data)

    if data.get('https') is None or data.get('domain') is None:
        r = {'status': 'error', 'reason': 'Wrong data is given'}
        logger.error(r)
        return await json_response(r, status=400)

    data.update({'author_id': request['user']['user_id']})
    r = await crawler_ms.make_nowait_request('index', data)
    logger.info(r)
    return await json_response(r)


async def stat(request):
    logger.info(request['user']['email'])
    cs = await CrawlerStats.objects.filter(author_id=request['user']['user_id'])
    r = {'status': 'ok', 'data': [await i.to_dict() async for i in cs]}
    logger.info(r)
    return await json_response(r)


async def search(request):
    logger.info(request.query)
    try:
        schema = SearchViewSchema()
        r = schema.dump({**request.query})
        q, limit, offset = r['q'], r['limit'], r['offset']
    except Exception as e:
        r = {'status': 'bad_request', 'reason': str(e)}
        logger.info(r)
        return await json_response(r)

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

    r = {'status': 'ok', 'data': response_data}
    logger.info(r)
    return await json_response(r)
