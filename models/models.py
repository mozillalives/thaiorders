
from webapp2_extras.appengine.auth.models import User
from google.appengine.ext.ndb import model
from google.appengine.ext import db

class User(User):
    """
    Universal user model. Can be used with App Engine's default users API,
    own auth or third party authentication methods (OpenId, OAuth etc).
    based on https://gist.github.com/kylefinley
    """

    #: Creation date.
    created = model.DateTimeProperty(auto_now_add=True)
    #: Modification date.
    updated = model.DateTimeProperty(auto_now=True)
    #: User defined unique name, also used as key_name.
    username = model.StringProperty(required=True)
    #: User Name
    name = model.StringProperty()
    #: User Last Name
    last_name = model.StringProperty()
    #: User email
    email = model.StringProperty(required=True)
    #: Password, only set for own authentication.
    password = model.StringProperty(required=True)
    #: User Country
    country = model.StringProperty()

    #: Authentication identifier according to the auth method in use. Examples:
    #: * own|username
    #: * gae|user_id
    #: * openid|identifier
    #: * twitter|username
    #: * facebook|username
    auth_id = model.StringProperty(repeated=True)
#    auth_id = model.StringProperty()
    # Flag to persist the auth across sessions for third party auth.
    auth_remember = model.BooleanProperty(default=False)

# TODO: use these methods for authentication and reset password
#    @classmethod
#    def get_by_username(cls, username):
#        return cls.query(cls.username == username).get()
#
#    @classmethod
#    def get_by_auth_id(cls, auth_id):
#        return cls.query(cls.auth_id == auth_id).get()
#

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


