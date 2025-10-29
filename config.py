import os

SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/diplomats"
     )
SECRET_KEY = os.environ.get("SECRET_KEY", "8f7b2c019b864a3b9eac53f4d8a4df12")
SQLALCHEMY_TRACK_MODIFICATIONS = False