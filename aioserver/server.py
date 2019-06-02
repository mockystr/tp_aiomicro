import jwt
from aiohttp import web
from aiohttp_jwt import JWTMiddleware
from aioserver.middlewares import TokenValidationMiddleware
from aioserver.routes import setup_routes
from aioserver.settings import sharable_secret


def main():
    token_whitelist = (r'/signup', r'/login', r'/search')
    app = web.Application(
        middlewares=[
            JWTMiddleware(secret_or_pub_key=sharable_secret,
                          request_property='user',
                          whitelist=token_whitelist),
            TokenValidationMiddleware(whitelist=token_whitelist)
        ]
    )
    setup_routes(app)
    web.run_app(app)


if __name__ == '__main__':
    main()
