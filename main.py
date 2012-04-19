#!/usr/bin/env python

import webapp2

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import memcache

from google.appengine.dist import use_library
use_library('django', '1.3')

from django import forms

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
    
    name = db.StringProperty()
    spiciness = db.StringProperty()
    meat = db.StringProperty()
    added_by = db.UserProperty()
    added_at = db.DateTimeProperty(auto_now_add=True)
    
    def __str__(self):
        return "%s %s %s for %s" % (self.name, self.spiciness, self.meat, self.added_by)
    
class ItemForm(forms.Form):
    name = forms.CharField()
    spiciness = forms.ChoiceField(choices=Item.SPICINESS)
    meat = forms.ChoiceField(choices=Item.MEATS)
    
class MainPage(webapp2.RequestHandler):
    def get(self):
        user = users.get_current_user()
        self.response.out.write('<html><body><h1>Thai Order!</h1>Ordering From: <b>Bangcok Cuisine</b><br />'
            'By: <b>Phil</b><br />At: <b>12:30pm</b><br /><ul>')
        all_items = memcache.get('all_items')
        if not all_items:
            all_items = Item.all()
            memcache.set('all_items', all_items)
        for item in all_items:
            if item.added_by == user:
                self.response.out.write('<li>%s <form method="POST" action="/cancel" style="display: inline">'
                    '<input type="hidden" name="item_id" value="%s" /><input type="submit" value="Cancel" />'
                    '</form></li>' % (item, item.key()))
            else:
                self.response.out.write('<li>%s</li>' % item)

        if not user:
            greeting = ("<a href=\"%s\">Please sign in to place your order</a>" % users.create_login_url("/"))
            self.response.out.write("</ul>%s</body></html>" % greeting)
        else:
            self.response.out.write('</ul><form method="POST" action="/"><table>')
            self.response.out.write(ItemForm())
            self.response.out.write('</table><input type="submit"></form></body></html>')
                    
    def post(self):
        user = users.get_current_user()
        form = ItemForm(self.request.POST)
        if form.is_valid() and user:
            item = Item(name=form['name'].data, spiciness=form['spiciness'].data,
                meat=form['meat'].data, added_by=user)
            item.put()
            all_items = Item.all()
            memcache.set('all_items', all_items)
            
        self.redirect("/")
        
class CancelItemPage(webapp2.RequestHandler):
    def post(self):
        user = users.get_current_user()
        item = Item.get(self.request.POST['item_id'])
        if item.added_by == user:
            item.delete()
            all_items = Item.all()
            memcache.set('all_items', all_items)
        self.redirect("/")
                    
app = webapp2.WSGIApplication([('/', MainPage), ('/cancel', CancelItemPage)], debug=True)
