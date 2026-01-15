# app/api.py
import datetime

from flask import Blueprint, request, jsonify
import logging

from flask import Blueprint, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from . import db
from .models import Game, Nation, Turn, Orders, Message, User

api = Blueprint("api", __name__, url_prefix="/api")

DEFAULT_NATIONS = [
    "England", "France", "Germany",
    "Italy", "Austria", "Russia", "Turkey"
]
DEFAULT_TURN_MINUTES = 5


def jerr(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code


def sanitize_html(string:str):
    return string.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def is_strong_password(password):
    # Example: at least 8 chars, contains a digit and a letter
    if len(password) < 8:
        return False
    if not any(c.isdigit() for c in password):
        return False
    if not any(c.isalpha() for c in password):
        return False
    return True


# ------- AUTH -------

@api.post("/register")
def register_user():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()
    if not username or not password:
        return jerr("username and password required")
    if User.query.filter_by(username=username).first():
        return jerr("username already exists", 409)
    if not is_strong_password(password):
        return jerr("Password too weak", 409)
    u = User(username=username)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    logging.info(F"New user {username}")
    return jsonify({"ok": True, "user_id": u.id}), 201


@api.post("/login")
def login_user_route():
    data = request.get_json(force=True, silent=True) or {}
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    u = User.query.filter_by(username=username).first()
    if not u or not u.check_password(password):
        return jerr("invalid credentials", 401)

    login_user(u)
    logging.info(F"User {username} login")
    return jsonify({"ok": True, "msg": f"logged in as {u.username}"})


@api.post("/logout")
@login_required
def logout_user_route():
    logging.info(F"User {current_user.id} login")
    logout_user()
    return jsonify({"ok": True, "msg": "logged out"})


# ------- GAME -------

@api.get("/games")
def list_games():
    games = Game.query.order_by(Game.started_at.desc()).limit(100).all()
    return jsonify({"ok": True, "data": [
        {"id": g.id, "name": g.name, "status": g.status, "started_at": g.started_at.isoformat()}
        for g in games
    ]})


@api.post("/games")
@login_required
def create_game():
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jerr("name is required")
    g = Game(name=sanitize_html(name))
    db.session.add(g)
    db.session.flush()  # get g.id
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
    for n in DEFAULT_NATIONS:
        db.session.add(Nation(name=n, game_id=g.id))
    db.session.commit()
    return jsonify({"ok": True, "id": g.id}), 201


@api.get("/games/<int:gid>")
@login_required
def get_game(gid):
    g = Game.query.get_or_404(gid)
    nations = Nation.query.filter_by(game_id=g.id).all()
    turns = Turn.query.filter_by(game_id=g.id).order_by(Turn.number).all()
    nation_owners: dict[int, str] = dict()
    for nation in nations:
        user = User.query.filter_by(id=nation.user_id).first()
        if user is not None:
            nation_owners.update({nation.id: user.username})
        else:
            nation_owners.update({nation.id: ''})
    return jsonify({
        "ok": True,
        "game": {"id": g.id, "name": g.name, "status": g.status},
        "nations": [{"id": n.id, "name": n.name, "user_id": nation_owners[n.id]} for n in nations],
        "turns": [{"id": t.id, "number": t.number, "phase": t.phase} for t in turns]
    })


# ------- NATION (join/assign) -------

@api.post("/games/<int:gid>/nations")
@login_required
def add_nation(gid):
    data = request.get_json(force=True, silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jerr("nation name is required")
    g = Game.query.get_or_404(gid)
    # ensure not already taken
    existing = Nation.query.filter_by(game_id=g.id, user_id=current_user.id).first()
    if existing:
        return jerr("You already joined this game.")
    n = Nation.query.filter_by(game_id=g.id, name=name).first()
    if not n:
        return jerr("Invalid nation name.")
    if n.user_id is not None:
        return jerr("Nation already taken.")
    n.user_id = current_user.id

    db.session.commit()
    return jsonify({"ok": True, "nation_id": n.id, "nation_name": n.name}), 201

# ------- ORDERS -------

@api.post("/turns/<int:tid>/orders")
@login_required
def post_order(tid):
    turn = Turn.query.get_or_404(tid)
    data = request.get_json(force=True, silent=True) or {}
    user: Nation = Nation.query.filter_by(game_id=turn.game_id).filter_by(user_id=current_user.id).first_or_404()
    payload = (data.get("payload") or "").strip()
    o = Orders(turn_id=turn.id, player_id=user.id, payload=sanitize_html(payload))
    db.session.add(o);
    db.session.commit()
    return jsonify({"ok": True, "order_id": o.id}), 201


# GET /api/turns/<int:tid>/orders
@api.get("/turns/<int:tid>/orders")
@login_required
def get_orders(tid):
    turn = Turn.query.get_or_404(tid)
    user: Nation = Nation.query.filter_by(game_id=turn.game_id).filter_by(user_id=current_user.id).first_or_404()
    current_turn = Turn.query.filter_by(game_id=turn.game_id).order_by(desc(Turn.number)).first_or_404()
    if turn.number == current_turn.number:
        orders = Orders.query.filter_by(turn_id=turn.id).filter_by(player_id=user.id).all()
    else:
        orders = Orders.query.filter_by(turn_id=turn.id).all()

    return jsonify({
        "ok": True,
        "turn_id": turn.id,
        "orders": [
            {
                "id": o.id,
                "player_id": o.player_id,
                "player_name": o.player.name if o.player else None,
                "payload": o.payload
            }
            for o in orders
        ]
    })


# ------- MESSAGE -------

@api.post("/games/<int:gid>/messages")
@login_required
def post_message(gid):
    g = Game.query.get_or_404(gid)
    data = request.get_json(force=True, silent=True) or {}
    user: Nation = Nation.query.filter_by(game_id=g.id).filter_by(user_id=current_user.id).first_or_404()
    scope = (data.get("recipient_scope") or "all").strip()
    if scope != "all":
        recipient = Nation.query.filter_by(game_id=g.id).filter_by(name=scope).first()
        if recipient is None:
            return jerr("nobody to send message to", 403)
        if recipient.id == user.id:
            return jerr("can't send messages to yourself", 403)
        scope = f"direct:{recipient.id}"
    text = (data.get("text") or "").strip()
    if not text:
        return jerr("text is required")
    msg = Message(game_id=g.id, sender_id=user.id, recipient_scope=scope, text=sanitize_html(text))
    db.session.add(msg);
    db.session.commit()
    return jsonify({"ok": True, "message_id": msg.id}), 201


# GET /api/games/<int:gid>/messages
@api.get("/games/<int:gid>/messages")
@login_required
def get_messages(gid):
    g = Game.query.get_or_404(gid)
    user:Nation = Nation.query.filter_by(game_id=g.id).filter_by(user_id=current_user.id).first()
    if user is None:
         return jerr("you have no access here", 403)
    messages_from_user = Message.query.filter_by(game_id=g.id).filter_by(sender_id=user.id).order_by(Message.created_at).all()
    messages_to_user = Message.query.filter_by(game_id=g.id).filter_by(recipient_scope=f"direct:{user.id}").order_by(Message.created_at).all()
    public_messages = Message.query.filter_by(game_id=g.id).filter(Message.sender_id != user.id,Message.recipient_scope=="all").all()
    messages = messages_from_user + messages_to_user + public_messages
    other_nations: list[Nation] = Nation.query.filter_by(game_id=g.id).filter(Nation.id != current_user.id).all()
    other_nations_dict = dict(zip([n.id for n in other_nations], [n.name for n in other_nations]))
    return jsonify({
        "ok": True,
        "messages": [
            {
                "sender_name": m.sender.name if m.sender else None,
                "recipient": "all" if m.recipient_scope == "all" else "me" if m.recipient_scope == f"direct:{user.id}" else f"{other_nations_dict[int(m.recipient_scope.removeprefix('direct:'))]}",
                "text": m.text,
                "created_at": m.created_at.isoformat()
            }
            for m in messages
        ]
    })


@api.get("/me")
@login_required
def get_current_user():
    return jsonify({
        "ok": True,
        "user": {"id": current_user.id, "username": current_user.username}
    })
