#!/usr/bin/env python

import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from django import forms

import jinja2
import os

jinja_environment = jinja2.Environment(autoescape=False,
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__) + '/templates'))

class Order(db.Model):
    
    STATUS = [
        ('open', 'Open'),
        ('closed', 'Closed')]
    
    TYPES = [
        ('thai', 'Thai'),
        ('other', 'Other'),
    ]
    
    status = db.StringProperty(default='open')
    place_type = db.StringProperty(default='thai')
    place_name = db.StringProperty()
    time = db.StringProperty()
    placed_by = db.StringProperty()
    added_by = db.UserProperty()
    added_at = db.DateTimeProperty(auto_now_add=True)
    
    def is_open(self):
        return self.status == 'open'
    
    def close(self):
        self.status = 'closed'
        
    def is_thai(self):
        return self.place_type == 'thai'
    
    def __str__(self):
        return "%s at %s by %s" % (self.place_name, self.time, self.placed_by)

class Item(db.Model):
    
    SPICINESS = [
        ('mild', 'Mild'),
        ('mild+', 'Mild +'),
        ('medium', 'Medium'),
        ('medium+', 'Medium +'),
        ('hot', 'Hot'),
        ('hot+', 'Hot +')]
    MEATS = [
        ('chicken', 'Chicken'),
        ('beef', 'Beef'),
        ('pork', 'Pork'),
        ('shrimp', 'Shrimp')]
    
    order = db.ReferenceProperty(Order)
    item_name = db.StringProperty()
    your_name = db.StringProperty()
    spiciness = db.StringProperty()
    meat = db.StringProperty()
    added_by = db.UserProperty()
    added_at = db.DateTimeProperty(auto_now_add=True)
    
    def __str__(self):
        if self.spiciness:
            return "%s %s %s for %s" % (self.item_name, self.meat, self.spiciness, self.your_name)
        else:
            return "%s for %s" % (self.item_name, self.your_name)

class OrderForm(forms.Form):
    place_name = forms.CharField(label="Where are you going?")
    placed_by = forms.CharField(label="Who's making the order?")
    time = forms.CharField(label="When?")
    kind = forms.ChoiceField(choices=Order.TYPES, label="What kind of food?")
    
class ItemForm(forms.Form):
    your_name = forms.CharField()
    item_name = forms.CharField()
    
class ThaiItemForm(ItemForm):
    meat = forms.ChoiceField(choices=Item.MEATS)
    spiciness = forms.ChoiceField(choices=Item.SPICINESS)
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        open_orders = Order.all()
        open_orders.filter("status =", "open")
        open_orders.order("-added_at")

        closed_orders = Order.all()
        closed_orders.filter("status =", "closed")
        closed_orders.order("-added_at")

        template_values = {
            'open_orders': open_orders,
            'closed_orders': closed_orders.fetch(limit=10),
            'order_form': OrderForm(),
            'login_url': users.create_login_url("/"),
            'user': users.get_current_user(),
        }
        template = jinja_environment.get_template('orders.html')
        self.response.out.write(template.render(template_values))
        
    def post(self):
        user = users.get_current_user()
        form = OrderForm(self.request.POST)
        if form.is_valid() and user:
            order = Order(place_name=form['place_name'].data, 
                placed_by=form['placed_by'].data,
                time=form['time'].data, 
                place_type=form['kind'].data, 
                added_by=user)
            order.put()

        self.redirect("/")
    
class OrderPage(webapp2.RequestHandler):
    def get(self, order_key):

        order = Order.get(order_key)
        all_items = Item.all()
        all_items.filter("order =", order)
                    
        template_values = {
            'order': order,
            'item_form': ThaiItemForm() if order.is_thai() else ItemForm(),
            'all_items': all_items,
            'login_url': users.create_login_url(),
            'user': users.get_current_user(),
        }
        
        template = jinja_environment.get_template('order.html')
        self.response.out.write(template.render(template_values))
                    
    def post(self, order_key):
        user = users.get_current_user()
        order = Order.get(order_key)
        form = ItemForm(self.request.POST)
        if form.is_valid() and user:
            item = Item(item_name=form['item_name'].data, order=order,
                your_name=form['your_name'].data, added_by=user)
            
            if 'spiciness' in form:
                item.spiciness = form['spiciness'].data
            if 'meat' in form:
                item.meat = form['meat'].data
                
            item.put()
            
        self.redirect("/order/%s" % order.key())
        
class CancelItemPage(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        try:
            item = Item.get(self.request.POST['item_id'])
            order_key = item.order.key()
            if item.added_by == user:
                item.delete()
                self.redirect("/order/%s" % order_key)
        except KeyError:
            item = Order.get(self.request.POST['order_id'])
            if item.added_by == user:
                item.close()
                item.put()
                self.redirect("/")
                    
app = webapp2.WSGIApplication([('/', MainPage), 
    ('/order/(.+)', OrderPage), 
    ('/cancel', CancelItemPage)], debug=True)
