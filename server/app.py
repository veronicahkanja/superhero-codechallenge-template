#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'


if __name__ == '__main__':
    app.run(port=5555, debug=True)


@app.route('/heroes', methods=['GET'])
def get_heroes():

    heroes = Hero.query.all()

    heroes_list = []

    for hero in heroes:
        heroes_list.append({
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name 
        })

    return make_response(heroes_list, 200)

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero_by_id(id):

    hero = Hero.query.get(id)

    if not hero:
        return make_response({"error": "Hero not found"}, 404)
    
    hero_data = {
        "id": hero.id,
        "name": hero.name,
        "super_name": hero.super_name,
        "hero_powers": [
            {
                "id": hp.id,
                "hero_id": hp.hero_id,
                "power_id": hp.power_id,
                "strength": hp.strength,
                "power": {
                    "id": hp.power.id,
                    "name": hp.power.name,
                    "description": hp.power.description
                }
            }
            for hp in hero.hero_powers
        ]
    }

    return make_response(hero_data, 200)
