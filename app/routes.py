from app import app
from app.models import Game


@app.route("/")
def index():
    return "test"


@app.route("/games")
def get_games():
    games = Game.query.all()
    return games
