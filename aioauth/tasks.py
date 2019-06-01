import datetime
import jwt
from validate_email import validate_email
from async_orm.models import User
from aioserver.utils import get_hashed_password
from aioauth.utils import check_password, get_hashed_password
from async_orm.models import Token
from aioserver.settings import TOKEN_EXPIRE_MINUTES, sharable_secret
from aioserver.exceptions import UserExists, ExpiredToken
from async_orm.exceptions import DoesNotExist


# class Task(type):
#     def __new__(mcs, name: str, bases, namespace):
#         return super().__new__(mcs, name.capitalize(), bases, namespace)


async def set_token(user):
    expire = datetime.datetime.now() + datetime.timedelta(minutes=TOKEN_EXPIRE_MINUTES)
    token = jwt.encode({'user_id': user.id, 'email': user.email, 'expire_date': str(expire)},
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


async def process_token(token):
    decoded_data = jwt.decode(token, sharable_secret)
    token_obj = await Token.objects.get(token=token)

    if token_obj.token != token:
        raise ValueError("Wrong token is given")

    expire_obj = datetime.datetime.strptime(decoded_data['expire_date'], '%Y-%m-%d %H:%M:%S.%f')

    return {'expired': expire_obj < datetime.datetime.now(), 'decoded_data': decoded_data}


class SignupTask:
    def __init__(self, email, password, name=None):
        self.email = email
        self.password = password
        self.name = name

    async def perform(self):
        if not validate_email(self.email):
            raise ValueError("Wrong email")

        if len(self.password) <= 4:
            raise ValueError("Password must be more than 4 characters.")

        now = datetime.datetime.now()
        if not await User.objects.filter(email=self.email).count():
            user = await User.objects.create(email=self.email,
                                             password=get_hashed_password(self.password.encode()).decode('utf-8'),
                                             name=self.name, created_date=now, last_login_date=now)
            return {'status': 'ok', 'data': await set_token(user)}
        else:
            raise UserExists


class LoginTask:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    async def perform(self):
        user = await User.objects.get(email=self.email)

        if not check_password(self.password.encode(), user.password.encode()):
            raise ValueError

        user.last_login_date = datetime.datetime.now()
        await user.save()
        return {'status': 'ok', 'data': await set_token(user)}


class ValidateTask:
    def __init__(self, token):
        self.token = token

    async def perform(self):
        token_data = await process_token(self.token)

        if token_data['expired'] is True:
            raise ExpiredToken

        user = await User.objects.get(email=token_data['decoded_data']['email'])
        return {'status': 'ok',
                'data': {key: value for key, value in (await user.to_dict()).items() if key != 'password'}}
