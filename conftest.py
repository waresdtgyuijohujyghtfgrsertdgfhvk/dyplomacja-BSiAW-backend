import pytest

from app import create_app, db
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
        yield


@pytest.fixture(scope='session')
def db(app, app_ctx):
    db.app = app
    db.create_all()

    yield db

    db.drop_all()
