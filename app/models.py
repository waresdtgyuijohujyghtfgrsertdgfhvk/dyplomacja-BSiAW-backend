from flask_login import UserMixin
from app import db, bcrypt, login_manager


GameStatus = db.Enum('lobby', 'active', 'finished', name='game_status')
TurnPhase  = db.Enum('spring','spring-disband','fall','fall-disband', name='turn_phase')


class User(UserMixin,db.Model):
    __tablename__ = "user"
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at    = db.Column(db.DateTime(timezone=True),
                              nullable=False, server_default=db.func.now())

    nations = db.relationship("Nation",
                              back_populates="user",
                              cascade="all, delete-orphan")

    def set_password(self, password: str):
        from app import bcrypt
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password: str):
        from app import bcrypt
        return bcrypt.check_password_hash(self.password_hash, password)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Game(db.Model):
    __tablename__ = "game"
    id         = db.Column(db.Integer, primary_key=True)
    name       = db.Column(db.String(128), nullable=False)
    status     = db.Column(GameStatus, nullable=False, server_default="lobby")
    started_at = db.Column(db.DateTime(timezone=True),
                           nullable=False, server_default=db.func.now())
    ends_at    = db.Column(db.DateTime(timezone=True))

    nations = db.relationship("Nation",
                              back_populates="game",
                              cascade="all, delete-orphan")
    turns   = db.relationship("Turn",
                              back_populates="game",
                              cascade="all, delete-orphan",
                              order_by="Turn.number")

    __table_args__ = (
        db.Index("idx_game_started", started_at.desc()),
    )


class Nation(db.Model):
    __tablename__ = "nation"
    id      = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer,
                        db.ForeignKey("game.id", ondelete="CASCADE"),
                        nullable=False)
    user_id = db.Column(db.Integer,
                        db.ForeignKey("user.id", ondelete="SET NULL"),
                        nullable=True)
    name    = db.Column(db.String(32))

    game   = db.relationship("Game", back_populates="nations")
    user   = db.relationship("User", back_populates="nations")
    orders = db.relationship("Orders", back_populates="player",
                             cascade="all, delete-orphan")
    messages_sent = db.relationship("Message", back_populates="sender",
                                    cascade="all, delete-orphan")


class Turn(db.Model):
    __tablename__ = "turn"
    id        = db.Column(db.Integer, primary_key=True)
    game_id   = db.Column(db.Integer,
                          db.ForeignKey("game.id", ondelete="CASCADE"),
                          nullable=False)
    number    = db.Column(db.Integer, nullable=False, server_default="1")
    state     = db.Column(db.String(4096))
    phase     = db.Column(TurnPhase, nullable=False, server_default="spring")

    game   = db.relationship("Game", back_populates="turns")
    orders = db.relationship("Orders", back_populates="turn",
                             cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("idx_turn_game_num", "game_id", "number"),
    )


class Orders(db.Model):
    __tablename__ = "orders"
    id        = db.Column(db.Integer, primary_key=True)
    turn_id   = db.Column(db.Integer,
                          db.ForeignKey("turn.id", ondelete="CASCADE"),
                          nullable=False)
    player_id = db.Column(db.Integer,
                          db.ForeignKey("nation.id", ondelete="CASCADE"),
                          nullable=False)
    payload   = db.Column(db.String(512))
    created_at= db.Column(db.DateTime(timezone=True),
                          nullable=False, server_default=db.func.now())

    turn   = db.relationship("Turn",   back_populates="orders")
    player = db.relationship("Nation", back_populates="orders")

    __table_args__ = (
        db.Index("idx_orders_turn", "turn_id"),
        db.Index("idx_orders_player", "player_id"),
    )


class Message(db.Model):
    __tablename__ = "message"
    id              = db.Column(db.Integer, primary_key=True)
    game_id         = db.Column(db.Integer,
                                db.ForeignKey("game.id", ondelete="CASCADE"),
                                nullable=False)
    sender_id       = db.Column(db.Integer,
                                db.ForeignKey("nation.id", ondelete="SET NULL"))
    recipient_scope = db.Column(db.String(32))   # 'all' | 'ally' | 'direct:<id>'
    text            = db.Column(db.String(2000), nullable=False)
    created_at      = db.Column(db.DateTime(timezone=True),
                                nullable=False, server_default=db.func.now())

    game   = db.relationship("Game")
    sender = db.relationship("Nation", back_populates="messages_sent")

    __table_args__ = (
        db.Index("idx_message_game_time", "game_id", "created_at"),
        db.CheckConstraint("length(text) > 0", name="chk_message_text_len"),
    )
