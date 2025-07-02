#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
import ipdb

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    
    def post(self):
        if not request.json.get('username') and request.json.get('password'):
            return make_response({'error': 'Username and password are required fields!'}, 422)
        
        try:
            fields = ['username', 'password', 'password_confirmation', 'bio', 'image_url']
            data = {f: request.json.get(f) for f in fields}
            
            user = User(
                username=data['username'],
                bio=data['bio'],
                image_url=data['image_url']
            )
            user.password_hash = data['password']
            db.session.add(user)
            db.session.commit()
            
            session['user_id'] = user.id
                        
            response_body = user.to_dict()
            
            return make_response(response_body, 201)
        
        except Exception:
            response_body = {'error': 'That username is already taken. Please choose another.'}
            return make_response(response_body, 422)
        

class CheckSession(Resource):
    
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        
        if user:
            response_body = user.to_dict()
            return make_response(response_body, 200)
        else:
            response_body = {'error': 'Users must login to view this content!'}
            return make_response(response_body, 401)
            

class Login(Resource):
    
    def post(self):
        username = request.json.get('username')
        password = request.json.get('password')
        user = User.query.filter(User.username == username).first()
        
        if not user:
            return make_response({'error': 'Invalid username'}, 401)
        
        if not user.authenticate(password):
            return make_response({'error': 'Invalid password.'}, 401)
        
        session['user_id'] = user.id
        
        response_body = user.to_dict()
        return make_response(response_body, 201)
    

class Logout(Resource):
    
    def delete(self):
        if not session.get('user_id'):
            return make_response({'error': 'You must be logged in to logout.'}, 401)
        
        session['user_id'] = None
        return make_response([], 204)


class RecipeIndex(Resource):
    
    def get(self):
        user = User.query.filter(User.id == session.get('user_id')).first()
        
        if not user:
            return make_response({'error': 'You must login to view recipes.'}, 401)
        
        response_body = [recipe.to_dict() for recipe in Recipe.query.all()]
        
        return make_response(response_body, 200)
    
    def post(self):
        
        user = User.query.filter(User.id == session.get('user_id')).first()
        
        if not user:
            return make_response({'error': 'You must login to post your recipes.'}, 401)
        
        try:
            fields = ['title', 'minutes_to_complete', 'instructions']
            data = {f: request.json.get(f) for f in fields}
            data['user_id'] = user.id
            
            recipe = Recipe(**data)
            db.session.add(recipe)
            db.session.commit()
            
            return make_response(recipe.to_dict(), 201)
        
        except Exception:
            return make_response({'error': 'All fields are mandatory and instructions must have at least 250 characters.'}, 422)


api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')


if __name__ == '__main__':
    app.run(port=5555, debug=True)