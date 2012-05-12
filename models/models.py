
from webapp2_extras.appengine.auth.models import User
from google.appengine.ext import ndb

class User(User):
    """
    Universal user model. Can be used with App Engine's default users API,
    own auth or third party authentication methods (OpenId, OAuth etc).
    based on https://gist.github.com/kylefinley
    """

    #: Creation date.
    created = ndb.model.DateTimeProperty(auto_now_add=True)
    #: Modification date.
    updated = ndb.model.DateTimeProperty(auto_now=True)
    #: User defined unique name, also used as key_name.
    username = ndb.model.StringProperty(required=True)
    #: User Name
    name = ndb.model.StringProperty()
    #: User Last Name
    last_name = ndb.model.StringProperty()
    #: User email
    email = ndb.model.StringProperty(required=True)
    #: Password, only set for own authentication.
    password = ndb.model.StringProperty(required=True)
    #: User Country
    country = ndb.model.StringProperty()

    #: Authentication identifier according to the auth method in use. Examples:
    #: * own|username
    #: * gae|user_id
    #: * openid|identifier
    #: * twitter|username
    #: * facebook|username
    auth_id = ndb.model.StringProperty(repeated=True)
#    auth_id = model.StringProperty()
    # Flag to persist the auth across sessions for third party auth.
    auth_remember = ndb.model.BooleanProperty(default=False)

# TODO: use these methods for authentication and reset password
#    @classmethod
#    def get_by_username(cls, username):
#        return cls.query(cls.username == username).get()
#
#    @classmethod
#    def get_by_auth_id(cls, auth_id):
#        return cls.query(cls.auth_id == auth_id).get()
#

class Order(ndb.Model):
    
    STATUS = [
        ('open', 'Open'),
        ('closed', 'Closed')]
    
    TYPES = [
        ('thai', 'Thai'),
        ('other', 'Other'),
    ]
    
    status = ndb.model.StringProperty(default='open')
    place_type = ndb.model.StringProperty(default='thai')
    place_name = ndb.model.StringProperty()
    time = ndb.model.StringProperty()
    placed_by = ndb.model.StringProperty()
    added_by = ndb.model.UserProperty()
    added_at = ndb.model.DateTimeProperty(auto_now_add=True)
    
    def is_open(self):
        return self.status == 'open'
    
    def close(self):
        self.status = 'closed'
        
    def is_thai(self):
        return self.place_type == 'thai'
    
    def __str__(self):
        return "%s at %s by %s" % (self.place_name, self.time, self.placed_by)

class Item(ndb.Model):
    
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
    
    order_key = ndb.model.KeyProperty(kind=Order)
    item_name = ndb.model.StringProperty()
    your_name = ndb.model.StringProperty()
    spiciness = ndb.model.StringProperty()
    meat = ndb.model.StringProperty()
    added_by = ndb.model.UserProperty()
    added_at = ndb.model.DateTimeProperty(auto_now_add=True)
    
    def __str__(self):
        if self.spiciness:
            return "%s %s %s for %s" % (self.item_name, self.meat, self.spiciness, self.your_name)
        else:
            return "%s for %s" % (self.item_name, self.your_name)


