# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../config.py', silent=True)
    db.init_app(app)
    migrate.init_app(app, db)

    @app.get("/")
    def root():
        return {"ok": True, "msg": "Diplomacy API", "endpoints": ["/healthz", "/api/games"]}

    @app.get("/healthz")
    def healthz(): return "OK", 200

    from app.api import api
    app.register_blueprint(api)

    return app


