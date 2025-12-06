def test_index_route_guest(client):
    response = client.get()
    assert response.status_code == 302
    assert response.headers['Location'] == '/login'


def test_healthz_route_guest(client):
    response = client.get("/healthz")
    assert response.status_code == 200


def test_api_games_route_guest(client, db):
    response = client.get("/api/games")
    assert response.status_code == 200

def test_register_route_guest(client, db):
    response = client.get("/register")
    assert response.status_code == 200
    assert b"Register" in response.data

def test_login_route_guest(client, db):
    response = client.get("/login")
    assert response.status_code == 200
    assert b"Register" in response.data

def test_lobby_route_guest(client, db):
    response = client.get("/lobby")
    assert response.status_code == 401

def test_game_route_guest(client, db):
    response = client.get("/game/1")
    assert response.status_code == 401

def test_map_route_guest(client, db):
    response = client.get("/mapsvg")
    assert response.status_code == 200