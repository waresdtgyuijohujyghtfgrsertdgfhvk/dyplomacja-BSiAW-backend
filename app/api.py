# app/api.py
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from . import db
from .models import Game, Nation, Turn, Orders, Message, User

api = Blueprint("api", __name__, url_prefix="/api")

def jerr(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code



@api.post("/users")
def create_users():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password_hash = (data.get("password_hash") or "").strip()
    u = User(username=username, password_hash=password_hash)
    db.session.add(u); db.session.commit()
    return jsonify({"ok": True,"uid": u.id}), 201

# ------- GAME -------

@api.get("/games")
def list_games():
    games = Game.query.order_by(Game.started_at.desc()).limit(100).all()
    return jsonify({"ok": True, "data": [
        {"id": g.id, "name": g.name, "status": g.status, "started_at": g.started_at.isoformat()}
        for g in games
    ]})

@api.post("/games")
def create_game():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jerr("name is required")
    g = Game(name=name)
    db.session.add(g)
    g.turns.append(Turn(state="""adr,,
aeg,,
alb,,
ank,tur,ftur
apu,ita,
arm,tur,
bal,,
bar,,
bel,,
ber,ger,ager
bla,,
boh,aus,
bre,fra,ffra
bud,aus,aaus
bul,,
bur,fra,
cly,bri,
con,tur,atur
den,,
eas,,
edi,bri,fbri
eng,,
fin,rus
gal,aus,
gas,fra,
gre,,
gol,,
gob,,
hel,,
hol,,
ion,,
iri,,
kie,ger,fger
lvp,bri,abri
lvn,rus,
lon,bri,fbri
mar,fra,afra
mao,,
mos,rus,arus
mun,ger,ager
nap,ita,fita
nao,,
naf,,
nth,,
nwy,,
nwg,,
par,fra,afra
pic,fra,
pie,fra,
por,,
pru,ger,
rom,ita,aita
ruh,ger,
rum,,
ser,,
sev,rus,frus
sil,ger,
ska,,
smy,tur,atur
spa,,
stp,rus,frus_sc
swe,,
syr,tur,
tri,aus,faus
tun,,
tus,ita,
trl,aus
tys,,
ukr,rus,
ven,ita,aita
vie,aus,aaus
wal,bri,
war,rus,arus
wes,,
yor,bri,"""))
    db.session.commit()
    return jsonify({"ok": True, "id": g.id}), 201

@api.get("/games/<int:gid>")
def get_game(gid):
    g = Game.query.get_or_404(gid)
    nations = Nation.query.filter_by(game_id=g.id).all()
    turns = Turn.query.filter_by(game_id=g.id).order_by(Turn.number).all()
    return jsonify({
        "ok": True,
        "game": {"id": g.id, "name": g.name, "status": g.status},
        "nations": [{"id": n.id, "name": n.name, "user_id": n.user_id} for n in nations],
        "turns": [{"id": t.id, "number": t.number, "phase": t.phase} for t in turns]
    })

# ------- NATION (join/assign) -------

@api.post("/games/<int:gid>/nations")
def add_nation(gid):
    g = Game.query.get_or_404(gid)
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    user_id = data.get("user_id")
    if not name:
        return jerr("nation name is required")
    n = Nation(game_id=g.id, user_id=user_id, name=name)
    db.session.add(n); db.session.commit()
    return jsonify({"ok": True, "nation_id": n.id}), 201

# ------- TURN -------

@api.post("/games/<int:gid>/turns")
def create_turn(gid):
    g = Game.query.get_or_404(gid)
    data = request.get_json(force=True, silent=True) or {}
    number = data.get("number")
    phase  = data.get("phase")
    if not isinstance(number, int) or number < 1:
        return jerr("number must be positive int")
    t = Turn(game_id=g.id, number=number, phase=phase or "planning")
    try:
        db.session.add(t); db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jerr("turn with this number already exists", 409)
    return jsonify({"ok": True, "turn_id": t.id}), 201

# ------- ORDERS -------

@api.post("/turns/<int:tid>/orders")
def post_order(tid):
    t = Turn.query.get_or_404(tid)
    data = request.get_json(force=True, silent=True) or {}
    player_id = data.get("player_id")
    order_type = (data.get("type") or "order").strip()
    payload = (data.get("payload") or "").strip()
    if not isinstance(player_id, int):
        return jerr("player_id must be int")

    n = Nation.query.get(player_id)
    if not n or n.game_id != t.game_id:
        return jerr("player must belong to the same game as turn", 409)

    o = Orders(turn_id=t.id, player_id=player_id, type=order_type, payload=payload)
    db.session.add(o); db.session.commit()
    return jsonify({"ok": True, "order_id": o.id}), 201

# ------- MESSAGE -------

@api.post("/games/<int:gid>/messages")
def post_message(gid):
    g = Game.query.get_or_404(gid)
    data = request.get_json(force=True, silent=True) or {}
    sender_id = data.get("sender_id")         # Nation.id
    scope     = (data.get("recipient_scope") or "all").strip()
    text      = (data.get("text") or "").strip()
    if not text:
        return jerr("text is required")
    msg = Message(game_id=g.id, sender_id=sender_id, recipient_scope=scope, text=text)
    db.session.add(msg); db.session.commit()
    return jsonify({"ok": True, "message_id": msg.id}), 201
