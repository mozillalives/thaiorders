# -*- coding: utf-8 -*-

"""
	A real simple app for using webapp2 with auth and session.

	It just covers the basics. Creating a user, login, logout
	and a decorator for protecting certain handlers.

    Routes are setup in routes.py and added in main.py

"""

import models.models as models
from google.appengine.ext import ndb
from webapp2_extras.appengine.auth.models import User
from webapp2_extras.auth import InvalidAuthIdError
from webapp2_extras.auth import InvalidPasswordError
from lib import utils
from lib.basehandler import BaseHandler
from lib.basehandler import user_required

# Just for Google Login
from google.appengine.api import users
from google.appengine.api import taskqueue
from webapp2_extras.appengine.users import login_required

from django import forms

class OrderForm(forms.Form):
    place_name = forms.CharField(label="Where are you going?")
    placed_by = forms.CharField(label="Who's making the order?")
    time = forms.CharField(label="When?")
    kind = forms.ChoiceField(choices=models.Order.TYPES, label="What kind of food?")
    
class ItemForm(forms.Form):
    your_name = forms.CharField()
    item_name = forms.CharField()
    
class ThaiItemForm(ItemForm):
    meat = forms.ChoiceField(choices=models.Item.MEATS)
    spiciness = forms.ChoiceField(choices=models.Item.SPICINESS)
    

class LogoutHandler(BaseHandler):
    """
         Destroy user session and redirect to login
    """

    def get(self):
        self.auth.unset_session()
        # User is logged out, let's try redirecting to login page
        try:
            message = "User is logged out." # Info message
            self.add_message(message, 'info')
            self.redirect(self.auth_config['login_url'])
        except (AttributeError, KeyError), e:
            return "User is logged out, but there was an error " \
                   "on the redirection."

class GoogleLoginHandler(BaseHandler):

    @login_required
    def get(self):
        # Login App Engine
        user = users.get_current_user()
        try:
            #TODO: work with the logout url for jQuery Mobile
            params = {
                "nickname" : user.nickname(),
                "userinfo_logout-url" : users.create_logout_url("/"),
                }
            return self.redirect("/")
        except (AttributeError, KeyError), e:
            return "Secure zone Google error: %s." % e

class MainPage(BaseHandler):
    def get(self):
        self.user = users.get_current_user()
        open_orders = models.Order.query(models.Order.status=="open")
        closed_orders = models.Order.query(models.Order.status=="closed").order(-models.Order.added_at).fetch(10)

        template_values = {
            'open_orders': open_orders,
            'closed_orders': closed_orders,
            'order_form': OrderForm(),
            'login_url': users.create_login_url("/"),
        }
        self.render_template('orders.html', **template_values)
        
    def post(self):
        user = users.get_current_user()
        form = OrderForm(self.request.POST)
        if form.is_valid() and user:
            order = models.Order(place_name=form['place_name'].data, 
                placed_by=form['placed_by'].data,
                time=form['time'].data, 
                place_type=form['kind'].data, 
                added_by=user)
            order.put()

        self.redirect("/")
    
class OrderPage(BaseHandler):
    def get(self, order_key):
        self.user = users.get_current_user()
        order = ndb.Key(urlsafe=order_key).get()
        all_items = models.Item.query(models.Item.order_key==order.key)           
        template_values = {
            'order': order,
            'item_form': ThaiItemForm() if order.is_thai() else ItemForm(),
            'all_items': all_items,
        }        
        self.render_template('order.html', **template_values)
                    
    def post(self, order_key):
        
        self.user = users.get_current_user()
        order = ndb.Key(urlsafe=order_key).get()
        
        if order.is_thai():
            form = ThaiItemForm(self.request.POST)
        else: 
            form = ItemForm(self.request.POST)
        
        if form.is_valid() and self.user:
            item = models.Item(item_name=form['item_name'].data, order_key=order.key,
                your_name=form['your_name'].data, added_by=self.user)

            if order.is_thai():
                item.spiciness = form['spiciness'].data
                item.meat = form['meat'].data
                
            item.put()
            
        self.redirect("/order/%s" % order.key.urlsafe())
        
class CancelItemPage(BaseHandler):
    def post(self):
        user = users.get_current_user()
        try:
            item = ndb.Key(urlsafe=self.request.POST['item_id']).get()
            order_key = item.order_key
            if item.added_by == user:
                item.key.delete()
                self.redirect("/order/%s" % order_key.urlsafe())
        except KeyError:
            item = ndb.Key(urlsafe=self.request.POST['order_id']).get()
            if item.added_by == user:
                item.close()
                item.put()
                self.redirect("/")