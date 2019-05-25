import jwt
from aiohttp import web
from aiohttp_jwt import JWTMiddleware

from routes import setup_routes
from settings import sharable_secret


def main():
    app = web.Application(middlewares=[
        JWTMiddleware(sharable_secret),
    ])
    setup_routes(app)
    web.run_app(app)


if __name__ == '__main__':
    main()
