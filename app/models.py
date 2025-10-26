from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db


class Player(db.Model):
    id: so.Mapped[int] = so.MappedColumn(primary_key=True)
    user_name: so.Mapped[str] = so.MappedColumn(sa.String(64), index=True, unique=True)


class Game(db.Model):
    id: so.Mapped[int] = so.MappedColumn(primary_key=True)
