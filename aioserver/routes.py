from aioserver.views import singup, login, current_user, index, stat, search


def setup_routes(app):
    # auth urls
    app.router.add_post('/singup', singup, name='singup')
    app.router.add_post('/login', login, name='login')
    app.router.add_get('/current', current_user, name='current_user')

    # crawler urls
    app.router.add_get('/search', search, name='search')
    app.router.add_post('/index', index, name='index')
    app.router.add_get('/stat', stat, name='stat')
