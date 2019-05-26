import asyncio
import pickle
import jwt
import datetime
import time
import aio_pika
from validate_email import validate_email
from .utils import inbound_name, outbound_name, check_password, get_hashed_password
from ..async_orm.models import User, Token, CrawlerStats
from ..aioserver.exceptions import UserExists, ExpiredToken
from ..async_orm.exceptions import DoesNotExist
from ..aioserver.settings import TOKEN_EXPIRE_MINUTES, sharable_secret


async def singup(data):
    try:
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

        return {'status': 'ok', 'data': await set_token(user)}
    except KeyError:
        return {'status': 'error', 'error_text': 'You must enter email and password', 'data': {}}
    except UserExists as e:
        return {'status': 'error', 'error_text': str(e), 'data': {}}
    except ValueError as e:
        return {'status': 'error', 'error_text': str(e), 'data': {}}


async def login(data):
    try:
        user = await User.objects.get(email=data['email'])

        if not check_password(data['password'].encode(), user.password.encode()):
            raise ValueError

        user.last_login_date = datetime.datetime.now()
        await user.save()
        return {'status': 'ok', 'data': await set_token(user)}
    except DoesNotExist as e:
        return {'status': 'error', 'error_text': str(e)}
    except (KeyError, ValueError):
        return {'status': 'error', 'error_text': 'Wrong credentials'}


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


async def validate(data):
    try:
        try:
            token_data = await process_token(data['token'])
        except (DoesNotExist, ValueError):
            return {'status': 'error', 'error_text': 'Wrong token is given'}

        if token_data['expired'] is True:
            raise ExpiredToken

        user = await User.objects.get(email=token_data['decoded_data']['email'])
        return {'status': 'ok',
                'data': {key: value for key, value in (await user.to_dict()).items() if key != 'password'}}
    except ExpiredToken as e:
        return {'status': 'error', 'error_text': str(e)}


async def process_token(token):
    decoded_data = jwt.decode(token, sharable_secret)
    token_obj = await Token.objects.get(token=token)

    if token_obj.token != token:
        raise ValueError

    expire_obj = datetime.datetime.strptime(decoded_data['expire_date'], '%Y-%m-%d %H:%M:%S.%f')

    return {'expired': expire_obj < datetime.datetime.now(), 'decoded_data': decoded_data}


async def main(loop):
    connection = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/", loop=loop)
    methods_dict = {'login': login, 'singup': singup, 'validate': validate}

    async with connection:
        channel = await connection.channel()
        inbound_queue = await channel.declare_queue(inbound_name)
        # outbound_queue = await channel.declare_queue(outbound_name)

        async with inbound_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    body = pickle.loads(message.body)

                    if body['type'] in methods_dict:
                        r = await methods_dict[body['type']](body['data'])
                        message_body = pickle.dumps({
                            'request_id': body['request_id'],
                            'type': body['type'],
                            'data': r
                        })

                        await channel.default_exchange.publish(
                            aio_pika.Message(body=message_body),
                            routing_key=outbound_name)
                    else:
                        message_body = pickle.dumps({
                            'request_id': body['request_id'],
                            'type': body['type'],
                            'data': {
                                'status': 'error',
                                'error_text': 'Wrong type'
                            }
                        })

                        await channel.default_exchange.publish(
                            aio_pika.Message(body=message_body),
                            routing_key=outbound_name)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print('[*] Waiting auth messages!')
    loop.run_until_complete(main(loop))
    loop.close()
