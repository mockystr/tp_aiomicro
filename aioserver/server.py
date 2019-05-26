import jwt
from aiohttp import web
from aiohttp_jwt import JWTMiddleware

from .routes import setup_routes
from .settings import sharable_secret


def main():
    app = web.Application(
        middlewares=[
            JWTMiddleware(secret_or_pub_key=sharable_secret,
                          request_property='user',
                          # credentials_required=False,
                          whitelist=(r'/singup', r'/login')),
        ]
    )
    setup_routes(app)
    web.run_app(app)


if __name__ == '__main__':
    main()
