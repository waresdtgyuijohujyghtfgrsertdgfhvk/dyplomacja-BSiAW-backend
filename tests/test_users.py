def test_user_register(client, db):
    user1 = {"username":"user1","password":"test_2025"}
    response = client.post('/api/register', json=user1,content_type='application/json')
    assert response.status_code == 201

def test_user_duplicate_register(client, db):
    user1 = {"username": "user1", "password": "test_2025"}
    response = client.post('/api/register', json=user1, content_type='application/json')
    assert response.status_code == 409

def test_user_login(client, db):
    user1 = {"username": "user1", "password": "test_2025"}
    response = client.post('/api/login', json=user1, content_type='application/json')
    assert response.status_code == 200
    response = client.get('/api/me')
    assert b'user1' in response.data
    response = client.post('/api/logout')
    assert b'out' in response.data

