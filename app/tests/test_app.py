
import sys
import os
import pytest

# Добавляем каталог app в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))

from create_app import create_app  # или просто из app
from db import db
from models import User



@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
    yield app
    db.drop_all()
    db.create_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register_user(client):
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }

    response = client.post('/api/register', json=data)
    assert response.status_code == 201
    assert b'"ok": true' in response.data

    user = User.query.filter_by(username='testuser').first()
    assert user is not None
    assert user.username == 'testuser'


def test_login_user(client):
    data = {
        'username': 'testuser',
        'password': 'testpassword'
    }

    client.post('/api/register', json=data)

    response = client.post('/api/login', json=data)
    assert response.status_code == 200
    assert b'"ok": true' in response.data


def test_create_game(client):
    data = {
        'name': 'Test Game'
    }

    response = client.post('/api/games', json=data)
    assert response.status_code == 201
    assert b'"ok": true' in response.data

    game = Game.query.filter_by(name='Test Game').first()
    assert game is not None
    assert game.name == 'Test Game'


def test_get_game(client):
    data = {'name': 'Test Game'}
    client.post('/api/games', json=data)

    game = Game.query.first()
    response = client.get(f'/api/games/{game.id}')
    assert response.status_code == 200
    assert b'"ok": true' in response.data
    assert b'Test Game' in response.data
def test_create_order(client):
    data = {'name': 'Test Game'}
    client.post('/api/games', json=data)
    game = Game.query.first()

    nation_data = {'name': 'England'}
    client.post(f'/api/games/{game.id}/nations', json=nation_data)
    nation = Nation.query.first()

    turn_data = {'number': 1, 'phase': 'spring'}
    client.post(f'/api/games/{game.id}/turns', json=turn_data)
    turn = Turn.query.first()

    order_data = {
        'player_id': nation.id,
        'payload': 'Some order payload'
    }
    response = client.post(f'/api/turns/{turn.id}/orders', json=order_data)
    assert response.status_code == 201
    assert b'"ok": true' in response.data
