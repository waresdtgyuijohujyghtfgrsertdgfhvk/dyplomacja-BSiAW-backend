# app/__init__.py
from flask import Flask, jsonify, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, login_required, current_user
from flask_vite import Vite

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
                # static_url_path='/static')

    # vite setup
    vite = Vite(app)
    app.config['VITE_AUTO_INSERT'] = True
    app.config['VITE_FOLDER_PATH'] = './vite'

    app.config.from_pyfile('../config.py', silent=True)
    #app.config.setdefault("SECRET_KEY", "change_this_secret")
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    login_manager.login_view = "api.login_user_route"

    @login_manager.unauthorized_handler
    def unauthorized():
        return jsonify({"ok": False, "error": "login required"}), 401

    @app.get("/healthz")
    def healthz(): return "OK", 200

    from app.api import api
    app.register_blueprint(api)

    @app.route("/")
    def index():
        if current_user.is_authenticated:
            return redirect("/lobby")
        else:
            return redirect("/login")

    @app.route("/login")
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

new_variable_for_ci_cd = 'CI/CD is working!'
