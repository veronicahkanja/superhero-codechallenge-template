#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_migrate import Migrate
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI",
    f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)

# -------------------------------
# Routes
# -------------------------------

@app.route("/")
def index():
    return "<h1>Code challenge</h1>"


# -------- HERO ROUTES -------- #

@app.route("/heroes", methods=["GET"])
def get_heroes():
    heroes = Hero.query.all()

    return make_response([
        {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name
        }
        for hero in heroes
    ], 200)


@app.route("/heroes/<int:id>", methods=["GET"])
def get_hero_by_id(id):
    hero = Hero.query.get(id)

    if not hero:
        return make_response({"error": "Hero not found"}, 404)

    return make_response({
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
    }, 200)


# -------- POWER ROUTES -------- #

@app.route("/powers", methods=["GET"])
def get_powers():
    powers = Power.query.all()

    return make_response([
        {
            "id": power.id,
            "name": power.name,
            "description": power.description
        }
        for power in powers
    ], 200)


@app.route("/powers/<int:id>", methods=["GET", "PATCH"])
def get_or_update_power(id):
    power = Power.query.get(id)

    # -------- 404 ERROR -------- #
    if not power:
        return make_response({"error": "Power not found"}, 404)

    # -------- PATCH UPDATE -------- #
    if request.method == "PATCH":
        data = request.get_json() or {}

        try:
            if "description" in data:
                desc = data["description"]

                if not isinstance(desc, str) or len(desc) < 20:
                    return make_response(
                        {"errors": ["validation errors"]},
                        400
                    )

                power.description = desc

            if "name" in data:
                name = data["name"]

                if not isinstance(name, str) or not name.strip():
                    return make_response(
                        {"errors": ["validation errors"]},
                        400
                    )

                power.name = name

            db.session.commit()

        except Exception as e:
            db.session.rollback()
            return make_response({"errors": [str(e)]}, 400)

    return make_response({
        "id": power.id,
        "name": power.name,
        "description": power.description
    }, 200)


# -------- HERO POWER CREATE -------- #

@app.route("/hero_powers", methods=["POST"])
def create_hero_power():
    data = request.get_json() or {}

    try:
        hero_power = HeroPower(
            strength=data["strength"],
            hero_id=data["hero_id"],
            power_id=data["power_id"]
        )

        db.session.add(hero_power)
        db.session.commit()

        return make_response({
            "id": hero_power.id,
            "strength": hero_power.strength,
            "hero_id": hero_power.hero_id,
            "power_id": hero_power.power_id,
            "hero": {
                "id": hero_power.hero.id,
                "name": hero_power.hero.name,
                "super_name": hero_power.hero.super_name
            },
            "power": {
                "id": hero_power.power.id,
                "name": hero_power.power.name,
                "description": hero_power.power.description
            }
        }, 200)

    except Exception as e:
        db.session.rollback()
        return make_response({"errors": [str(e)]}, 400)


if __name__ == "__main__":
    app.run(port=5555, debug=True)
    