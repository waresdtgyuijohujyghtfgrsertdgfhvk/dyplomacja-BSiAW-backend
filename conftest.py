import pytest

from app import create_app, db as _db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


@pytest.fixture(scope='session')
def app():
    app = create_app()
    app.config.update({'TESTING': True})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture(scope='session')
def app_ctx(app):
    with app.app_context():
        yield app.app_context()



@pytest.fixture(scope='session')
def db(app, app_ctx):
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.session.close()
    _db.drop_all()

@pytest.fixture(scope='session')
def users(app, db):
    client = app.test_client()
    user = {"username": "userA", "password": "test_2025A"}
    response = client.post('/api/register', json=user, content_type='application/json')
    user = {"username": "userB", "password": "test_2025B"}
    response = client.post('/api/register', json=user, content_type='application/json')
    user = {"username": "userC", "password": "test_2025C"}
    response = client.post('/api/register', json=user, content_type='application/json')
    user = {"username": "userD", "password": "test_2025D"}
    response = client.post('/api/register', json=user, content_type='application/json')
    user = {"username": "userE", "password": "test_2025E"}
    response = client.post('/api/register', json=user, content_type='application/json')
    user = {"username": "userF", "password": "test_2025F"}
    response = client.post('/api/register', json=user, content_type='application/json')