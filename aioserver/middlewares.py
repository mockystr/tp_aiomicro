import asyncio
import jwt
from aiohttp import web
import aiohttp_jwt
from aioserver.utils import auth_ms, json_response, logger


def TokenValidationMiddleware(whitelist=(), request_propery='user'):
    @web.middleware
    async def token_validation_middleware(request, handler):
        if request.path in whitelist:
            return await handler(request)

        try:
            scheme, token = request.headers.get('Authorization').strip().split(' ')
        except ValueError:
            raise web.HTTPForbidden(reason='Invalid authorization header', )

        data = {'token': token}
        validate_response = await auth_ms.make_request('validate', data=data, timeout=5)

        if validate_response['status'] != 'ok':
            logger.error(validate_response)
            return await json_response(validate_response, status=400)

        logger.info(validate_response)
        request[request_propery]['split_token'] = token
        return await handler(request)

    return token_validation_middleware
