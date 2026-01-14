# smoke_test_models.py
import os
from sqlalchemy.exc import IntegrityError
from app import create_app, db
import app.models as m  # ВАЖНО: имортируй модели, чтобы SQLAlchemy их увидел
from sqlalchemy.exc import IntegrityError, DataError

# 1) Контекст приложения
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/diplomats")
app = create_app()
app.app_context().push()

# 2) Чистая схема для теста (в проде используй Alembic!)
db.drop_all()
db.create_all()

def ok(msg): print("✔", msg)
def bad(msg): print("✘", msg)

# 3) Создадим базовые сущности
u = m.User(username="host", password_hash="x")
g = m.Game(name="Demo", status="lobby")
db.session.add_all([u, g]); db.session.commit()
ok(f"Созданы User#{u.id}, Game#{g.id}")

# nation (страна/игрок) привязана к игре и пользователю
n = m.Nation(game_id=g.id, user_id=u.id, name="England")
db.session.add(n); db.session.commit()
ok(f"Создана Nation#{n.id} → game {n.game_id}, user {n.user_id}")

# turn (тур) №1
t1 = m.Turn(game_id=g.id, number=1, phase="planning")
db.session.add(t1); db.session.commit()
ok(f"Создан Turn#{t1.id} №{t1.number} для Game#{g.id}")

# orders (приказ) от нации в этом туре
o1 = m.Orders(turn_id=t1.id, player_id=n.id, type="order", payload="MOVE A PAR-BUR")
db.session.add(o1); db.session.commit()
ok(f"Создан Orders#{o1.id} → turn {o1.turn_id}, nation {o1.player_id}")

# message (чат)
msg = m.Message(game_id=g.id, sender_id=n.id, recipient_scope="all", text="Привет!")
db.session.add(msg); db.session.commit()
ok(f"Создан Message#{msg.id} в Game#{g.id}")

# 4) Проверим UNIQUE и CHECK/ENUM
# 4.1 username UNIQUE
try:
    db.session.add(m.User(username="host", password_hash="y"))
    db.session.commit()
    bad("ДОЖДАЛИСЬ? username UNIQUE НЕ сработал")
except IntegrityError:
    db.session.rollback()
    ok("UNIQUE(username) работает")

# 4.2 UNIQUE (game_id, number) для Turn
try:
    db.session.add(m.Turn(game_id=g.id, number=1, phase="planning"))
    db.session.commit()
    bad("UNIQUE(game_id, number) НЕ сработал (дубликат тёрна)")
except IntegrityError:
    db.session.rollback()
    ok("UNIQUE(game_id, number) работает")
# 4.3 ENUM/Check для phase/status (плохое значение фазы)
try:
    db.session.add(m.Turn(game_id=g.id, number=2, phase="bad_phase"))
    db.session.commit()
    print("✘ ENUM/Check для turn.phase НЕ сработал")
except (IntegrityError, DataError):  # <- важно: ловим и DataError
    db.session.rollback()
    print("✔ ENUM/Check для turn.phase работает")

# 5) Проверим каскады
# Удалим игру и убедимся, что связанные записи пропали/обнулились
db.session.delete(g); db.session.commit()

# Должны исчезнуть: Nations, Turns, Orders, Messages (игра удалена каскадом)
left_nations = m.Nation.query.all()
left_turns   = m.Turn.query.all()
left_orders  = m.Orders.query.all()
left_msgs    = m.Message.query.all()

if not left_nations and not left_turns and not left_orders and not left_msgs:
    ok("CASCADE удаление от Game сработало (все зависимости ушли)")
else:
    bad(f"Остатки после каскада: nations={len(left_nations)}, turns={len(left_turns)}, orders={len(left_orders)}, msgs={len(left_msgs)}")
