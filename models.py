from app import app,db
from itsdangerous import Serializer
from sqlalchemy import Enum



class Suggestions(db.Model):
    tablename = ['Suggestions']

    id = db.Column(db.Integer, primary_key=True)
    suggestion = db.Column(db.String, nullable=False)
    slug = db.Column(db.String, nullable=False)
    total = db.Column(db.Integer)
    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'))


    def __repr__(self):
        return f"Suggestion('id: {self.id}', 'suggestion:{self.suggestion}', 'slug:{self.slug}')"
    
class Listing(db.Model):
    tablename = ['Listing']

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String)
    location = db.Column(db.String)
    locationTag = db.Column(db.String)
    images = db.relationship('Image', backref='listing', lazy=True)
    suggestions = db.relationship('Suggestions', backref='listing', lazy=True)

    def __repr__(self):
        return f"Listing('id: {self.id}', 'name:{self.suggestion}', 'location:{self.location}')"

class SubListing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    description = db.Column(db.String)
    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'))
    superListing = db.Column(db.Integer, db.ForeignKey('listing.name'))
    
    def __repr__(self):
        return f"SubListing('id: {self.id}', 'name:{self.name}', 'superlisting:{self.listingId}'. '{self.superListing}')"

class Image(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String, nullable=False)
    listingId = db.Column(db.Integer, db.ForeignKey('listing.id'), nullable=False)

    def __repr__(self):
        return f"Listing('id: {self.id}', 'name:{self.suggestion}', 'location:{self.location}')" 

class LocationTagEnum(Enum):
    on_campus = 'on_campus'
    off_campus = 'off_campus'


class User(db.Model):
    """Model for user accounts."""
    __tablename__ = 'users'

    name = db.Column(db.String)
    phone = db.Column(db.String)
    chatId = db.Column(db.String)
    telegramBot = db.Column(db.String)
    balance = db.Column(db.String, default=0)
    type = db.Column(db.String, default="payment")
    message = db.Column(db.String)
    callbackUrl = db.Column(db.String)
    availablebalance = db.Column(db.Float, default=0)
    percentage = db.Column(db.Float, default=0)
    role = db.Column(db.String, default="user")
    id = db.Column(db.Integer,primary_key=True)
    dailyDisbursal = db.Column(db.Boolean, default=False)
    username = db.Column(db.String,nullable=False,unique=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password = db.Column(db.String(), primary_key=False, unique=False, nullable=False)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return '<User {}>'.format(self.username)

