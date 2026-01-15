# app/__init__.py
import logging

from flask import Flask, jsonify, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user
from flask_vite import Vite
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_apscheduler import APScheduler


import sys
from logging.config import dictConfig
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
scheduler = APScheduler()

def create_app():


    dictConfig({
        'version': 1,
        'formatters': {'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }},
        'handlers': {'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # <-- Solution
            'formatter': 'default'
        }},
        'root': {
            'level': 'INFO',
            'handlers': ['wsgi']
        }
    })

    app = Flask(__name__)
    app.config.from_pyfile('../config.py', silent=True)
    @app.after_request
    def set_security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self'; "
            f"connect-src 'self' http://localhost:5173 https://{app.config['DOMAIN']};"
            "frame-ancestors 'none'; "
        )
        return response
        # static_url_path='/static')

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per minute"],
        storage_uri="memory://",
    )
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                f"https://{app.config['DOMAIN']}",
                "http://localhost:5173"
            ]
        },
        r"/*": {
            "origins": [
                f"https://{app.config['DOMAIN']}",
                "http://localhost:5173"
            ]
        }
    })

    # from .routes import api_bp
    # app.register_blueprint(api_bp, url_prefix="/api")
    # vite setup
    vite = Vite(app)
    app.config['VITE_AUTO_INSERT'] = True
    app.config['VITE_FOLDER_PATH'] = './vite'

    # app.config.setdefault("SECRET_KEY", "change_this_secret")
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    scheduler.init_app(app)
    scheduler.start()

    login_manager.login_view = "api.login_user_route"

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"ok": False, "error": "login required"}), 401

    @app.get("/healthz")
    def healthz():
        return "OK", 200

    # from app.api import api
    # app.register_blueprint(api)
    from .api import api
    app.register_blueprint(api)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect("/lobby")
        else:
            return redirect("/login")

    @app.route("/rate-test", methods=["GET"])
    @limiter.limit("5 per minute")
    def rate_test():
        return {"ok": True}, 200

    @app.route("/login")
    @limiter.limit("5 per minute")
    def login_page():
        return render_template("login.html")

    @app.route("/register")
    def register_page():
        return render_template("register.html")

    @app.route("/lobby")
    @login_required
    def lobby_page():
        return render_template("lobby.html")

    @app.route('/game/<int:gid>')
    @login_required
    def game_page(gid):
        return render_template('game.html')

    @app.route("/mapsvg")
    def handle_svg():
        return render_template("diplomacy_wiki.svg")

    return app
from app import arbitration