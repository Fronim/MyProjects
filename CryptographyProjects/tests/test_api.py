def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b"Cryptography Projects" in response.data


def test_api_generate_success(client):
    payload = {
        "m": 2147483641,
        "a": 16384,
        "c": 75025,
        "x0": 41,
        "count": 100
    }
    response = client.post('/api/v1/generate', json=payload)
    data = response.get_json()

    assert response.status_code == 200
    assert 'pi_estimate' in data['statistics']
    assert len(data['data_sample']) <= 50


def test_api_generate_invalid_types(client):
    payload = {
        "m": "not_a_number",
        "a": 16384
    }
    response = client.post('/api/v1/generate', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "Некоректний формат даних" in data['error']


def test_api_generate_empty_payload(client):
    response = client.post('/api/v1/generate', json={})
    data = response.get_json()

    assert response.status_code == 400
    assert "Відсутні дані" in data['error']


def test_api_generate_negative_count(client):
    payload = {
        "count": -5,
        "m": 100
    }
    response = client.post('/api/v1/generate', json=payload)
    data = response.get_json()

    assert response.status_code == 400
    assert "мають бути додатними" in data['error']

def test_lcg_page(client):
    response = client.get('/lcg')
    assert response.status_code == 200
    assert b"PRNG Analysis Tool" in response.data or b"Linear Congruential Generator" in response.data

def test_api_period_success(client):
    payload = {"m": 100, "a": 3, "c": 1, "x0": 10}
    response = client.post('/api/v1/period', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert 'period' in data
    assert data['period'] == 20

def test_api_period_too_large(client):
    payload = {"m": 2147483641, "a": 16384, "c": 75025, "x0": 41}
    response = client.post('/api/v1/period', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert 'message' in data

def test_api_period_invalid_data(client):
    response = client.post('/api/v1/period', json={"m": "bad_string"})
    assert response.status_code == 400

def test_api_period_empty_payload(client):
    response = client.post('/api/v1/period', json={})
    assert response.status_code == 400
def test_api_system_generate_success(client):
    payload = {"m": 2147483641, "count": 100}
    response = client.post('/api/v1/system_generate', json=payload)
    data = response.get_json()
    assert response.status_code == 200
    assert 'statistics' in data
    assert 'chart_data' in data
    assert len(data['chart_data']) == 100