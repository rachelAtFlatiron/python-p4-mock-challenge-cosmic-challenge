#!/usr/bin/env python3

from models import db, Scientist, Mission, Planet
from flask_restful import Api, Resource
from flask_migrate import Migrate
from flask import Flask, make_response, jsonify, request
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)

@app.route('/')
def home():
    return ''

class Scientists(Resource):
    def get(self):
        q = Scientist.query.all()

        q_list = [s.to_dict(only=('id', 'name', 'field_of_study')) for s in q]

        return make_response(q_list)
    
    def post(self):
        data = request.get_json()
        try:
            scientist = Scientist(
                name=data.get('name'),
                field_of_study=data.get('field_of_study')
            )
            db.session.add(scientist)
            db.session.commit()

            return make_response(scientist.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Scientists, '/scientists')

class OneScientist(Resource):
    def get(self, id):
        q = Scientist.query.filter_by(id=id).first()
        if not q:
            return make_response({'error': 'Scientist not found'}, 404)
        return make_response(q.to_dict())
    
    def patch(self, id):
        q = Scientist.query.filter_by(id=id).first()
        if not q:
            return make_response({'error': 'Scientist not found'}, 404)
        try:
            data = request.get_json()
            for attr in data:
                setattr(q, attr, data.get(attr))
            db.session.add(q)
            db.session.commit()

            return make_response(q.to_dict(), 202)
        except ValueError:
           return({"errors": ["validation errors"]}, 400) 
        
    def delete(self, id):
        q = Scientist.query.filter_by(id=id).first()
        if not q:
            return make_response({'error': 'Scientist not found'}, 404)
        try:
            db.session.delete(q)
            db.session.commit()
            return make_response({}, 204)
        except:
            return make_response({})

api.add_resource(OneScientist, '/scientists/<int:id>')

class Planets(Resource):
    def get(self):
        q = Planet.query.all()
        q_list = [p.to_dict(only=('id', 'name', 'distance_from_earth', 'nearest_star')) for p in q]

        return make_response(q_list)
api.add_resource(Planets, '/planets')

class Missions(Resource):
    def post(self):
        data = request.get_json()

        try:
            mission = Mission(
                name = data.get('name'),
                scientist_id = data.get('scientist_id'),
                planet_id = data.get('planet_id')
            )

            db.session.add(mission)
            db.session.commit()
            return make_response(mission.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)

api.add_resource(Missions, '/missions')

if __name__ == '__main__':
    app.run(port=5555, debug=True)
