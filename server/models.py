from sqlalchemy.orm import validates
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy_serializer import SerializerMixin

from config import db, bcrypt

class User(db.Model, SerializerMixin):
    __tablename__ = 'users'
    
    serialize_rules = ('-_password_hash', '-recipes.user')

    # user attributes / table columns
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True)
    bio = db.Column(db.String)
    image_url = db.Column(db.String)
    _password_hash = db.Column(db.String)
    
    # user relationships
    recipes = db.relationship('Recipe', back_populates='user')
    
    
    # password getter and setter
    @hybrid_property
    def password_hash(self):
        raise AttributeError('Passwords are off limits!')
    
    @password_hash.setter
    def password_hash(self, password):
        password_hash = bcrypt.generate_password_hash(
            password.encode('UTF-8'))
        self._password_hash = password_hash.decode('UTF-8')
    
        
    # password authentication
    def authenticate(self, password):
        return bcrypt.check_password_hash(self._password_hash, password.encode('UTF-8'))
    
    
    def __repr__(self):
        return f'<<< USER: {self.username} >>>'


class Recipe(db.Model, SerializerMixin):
    __tablename__ = 'recipes'
    
    # recipe attributes / table columns
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    instructions = db.Column(db.String, nullable=False)
    minutes_to_complete = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # recipe relationships
    user = db.relationship('User', back_populates='recipes')
    
    # constraints
    __table_args__ = (db.CheckConstraint('length(instructions) >= 50'),)
    
    
    def __repr__(self):
        return f'<<< RECIPE: {self.title} >>>'