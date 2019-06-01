import jwt
from aiohttp import web
from aiohttp_jwt import JWTMiddleware

from aioserver.routes import setup_routes
from aioserver.settings import sharable_secret


def main():
    app = web.Application(
        middlewares=[
            JWTMiddleware(secret_or_pub_key=sharable_secret,
                          request_property='user',
                          whitelist=(r'/singup', r'/login', r'/search')),
        ]
    )
    setup_routes(app)
    web.run_app(app)


if __name__ == '__main__':
    main()
