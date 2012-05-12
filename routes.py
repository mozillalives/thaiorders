"""
Using redirect route instead of simple routes since it supports strict_slash
Simple route: http://webapp-improved.appspot.com/guide/routing.html#simple-routes
RedirectRoute: http://webapp-improved.appspot.com/api/webapp2_extras/routes.html#webapp2_extras.routes.RedirectRoute
"""

from webapp2_extras.routes import RedirectRoute
from web.handlers import MainPage, OrderPage, CancelItemPage, LogoutHandler, GoogleLoginHandler

_routes = [
    RedirectRoute('/login/', GoogleLoginHandler, name='login', strict_slash=True),
    RedirectRoute('/logout/', LogoutHandler, name='logout', strict_slash=True),
    RedirectRoute('/cancel', CancelItemPage, name='cancel', strict_slash=True),
    RedirectRoute('/order/<order_key:.+>', OrderPage, name='order', strict_slash=True),
    RedirectRoute('/', MainPage, name='home', strict_slash=True)
]

def get_routes():
    return _routes

def add_routes(app):
    for r in _routes:
        app.router.add(r)
