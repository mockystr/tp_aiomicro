from views import index, search, singup


def setup_routes(app):
    app.router.add_get('/', index, name='index')
    app.router.add_post('/singup', singup, name='singup')
    app.router.add_get('/api/v1/search', search, name='search')
