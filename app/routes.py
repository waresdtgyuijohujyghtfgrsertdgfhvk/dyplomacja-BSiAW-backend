from app.models import Game
from flask import Blueprint
api_bp = Blueprint("api", __name__)

@api_bp.route("/test")
def test():
    return {"status": "ok"}
@api_bp.route("/")
def index():
    return "test"


@api_bp.route("/games")
def get_games():
    games = Game.query.all()
    return games
