from .views import search, singup, login, current_user


def setup_routes(app):
    app.router.add_post('/singup', singup, name='singup')
    app.router.add_post('/login', login, name='login')

    app.router.add_get('/current', current_user, name='current_user')
    app.router.add_get('/search', search, name='search')
