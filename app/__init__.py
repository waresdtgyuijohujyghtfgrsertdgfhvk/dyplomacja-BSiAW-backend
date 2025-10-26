# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/diplomats?connect_timeout=5"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    @app.get("/")
    def root():
        return {"ok": True, "msg": "Diplomats API", "endpoints": ["/healthz", "/api/games"]}

    @app.get("/healthz")
    def healthz(): return "OK", 200

    from app.api import api
    app.register_blueprint(api)

    return app
