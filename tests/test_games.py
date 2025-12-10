def test_create_game(client,db,users):
    response = client.post("api/games",json={"name":"test1"},content_type="application/json")
    assert response.status_code == 401
    user = {"username": "userA", "password": "test_2025A"}
    response = client.post('/api/login', json=user, content_type='application/json')
    response = client.post("api/games", json={"name": "testowa"}, content_type="application/json")
    assert response.status_code == 201
    response = client.post("api/games", content_type="application/json")
    assert response.status_code == 400
    assert b"required" in response.data

    response = client.post('/api/logout')
    assert b'out' in response.data


def test_game_exists(client,db,users):
    response = client.get("/api/games")
    assert response.status_code == 200
    assert b"testowa" in response.data
    assert b"test1" not in response.data


def test_add_players_to_game(client,db,users):
    response = client.post("api/games/1/nations")
    assert response.status_code == 401
    user = {"username": "userA", "password": "test_2025A"}
    response = client.post('/api/login', json=user, content_type='application/json')
    assert response.status_code == 200
    response = client.post("api/games/1/nations",json={}, content_type='application/json')
    assert b'is required' in response.data
    response = client.post("api/games/1/nations", json={"name":"England"}, content_type='application/json')
    assert b'England' in response.data
    response = client.post("api/games/1/nations", json={"name": "England"}, content_type='application/json')
    assert b'already' in response.data
    response = client.post('/api/logout')
    assert b'out' in response.data
    user = {"username": "userB", "password": "test_2025B"}
    response = client.post('/api/login', json=user, content_type='application/json')
    assert response.status_code == 200
    response = client.post("api/games/1/nations", json={"name": "England"}, content_type='application/json')
    assert b'taken' in response.data
    response = client.post("api/games/1/nations", json={"name": "German"}, content_type='application/json')
    assert b'Invalid' in response.data
    response = client.post("api/games/1/nations", json={"name": "Germany"}, content_type='application/json')
    assert b'Germany' in response.data
    response = client.post('/api/logout')
    assert b'out' in response.data

def test_create_order(client):
    user = {"username": "userA", "password": "test_2025A"}
    response = client.post('/api/login', json=user, content_type='application/json')
    assert response.status_code == 200

    order_data = {
        'player_id': 1,
        'payload': 'Some order payload'
    }
    response = client.post(f'/api/turns/1/orders', json=order_data)
    assert response.status_code == 201
    assert b'"ok":true' in response.data
    response = client.post('/api/logout')
    assert b'out' in response.data