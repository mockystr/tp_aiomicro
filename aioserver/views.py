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


async def singup(request):
    try:
        data = await request.json()

        if await (await User.objects.filter(email=data['email'])).count():
            raise UserExists()

        if not validate_email(data['email']):
            raise ValueError("Wrong email")

        if len(data['password']) <= 4:
            raise ValueError("Password must be more than 4 characters.")

        now = datetime.datetime.now()
        user = await User.objects.create(email=data['email'],
                                         password=get_hashed_password(data['password'].encode()).decode('utf-8'),
                                         name=data.get('name'), created_date=now, last_login_date=now)

        return await json_response({'status': 'ok', 'data': await set_token(user)})
    except KeyError:
        return await json_response({'status': 'error', 'error_text': 'You must enter email and password',
                                    'data': {}})
    except UserExists as e:
        return await json_response({'status': 'error', 'error_text': str(e),
                                    'data': {}})
    except ValueError as e:
        return await json_response({'status': 'error', 'error_text': str(e),
                                    'data': {}})


async def login(request):
    try:
        data = await request.json()
        user = await User.objects.get(email=data['email'])

        if not check_password(data['password'].encode(), user.password.encode()):
            raise ValueError

        user.last_login_date = datetime.datetime.now()
        await user.save()
        return await json_response({'status': 'ok', 'data': await set_token(user)})
    except DoesNotExist as e:
        return await json_response({'status': 'error', 'error_text': str(e)})
    except (KeyError, ValueError) as e:
        return await json_response({'status': 'error', 'error_text': 'Wrong credentials'})


async def set_token(user):
    expire = datetime.datetime.now() + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({'email': user.email, 'password': user.password, 'expire_date': str(expire)},
                       key=sharable_secret).decode('utf-8')

    try:
        token_obj = await Token.objects.get(user_id=user.id)
        token_obj.token, token_obj.user_id, token_obj.expire_date = token, user.id, expire
        await token_obj.save()
    except DoesNotExist:
        await Token.objects.create(token=token,
                                   user_id=user.id,
                                   expire_date=expire)
    return {'token': token, 'expire': str(expire)}


async def process_token(request):
    token = request.headers.get('authorization').split(' ')[1]
    decoded_data = jwt.decode(token, sharable_secret)
    token_user = await User.objects.get(email=request['user']['email'])
    token_obj = await Token.objects.get(user_id=token_user.id)

    if token_obj.token != token:
        raise ValueError

    expire_obj = datetime.datetime.strptime(decoded_data['expire_date'], '%Y-%m-%d %H:%M:%S.%f')

    return {'expired': expire_obj < datetime.datetime.now(), 'decoded_data': decoded_data}


async def current_user(request):
    auth = AuthMS()

    await auth.make_request('current_user', {'id': 1})

    try:
        try:
            token_data = await process_token(request)
        except (DoesNotExist, ValueError):
            return await json_response({'status': 'error', 'error_text': 'Wrong token is given'})

        if token_data['expired'] is True:
            raise ExpiredToken

        user = await User.objects.get(email=token_data['decoded_data']['email'])
        return await json_response({'status': 'ok', 'data': await user.to_dict()})
    except ExpiredToken as e:
        return await json_response({'status': 'error', 'error_text': str(e)})


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
