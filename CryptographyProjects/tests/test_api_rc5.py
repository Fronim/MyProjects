import io
import json
from app import app
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_api_rc5_missing_file(client):
    data = {
        'password': 'pass',
        'action': 'encrypt'
    }
    response = client.post('/api/v1/rc5/process', data=data, content_type='multipart/form-data')
    assert response.status_code == 400
    assert b"No file uploaded" in response.data


def test_api_rc5_missing_password(client):
    data = {
        'file': (io.BytesIO(b"dummy data"), 'test.txt'),
        'action': 'encrypt'
    }
    response = client.post('/api/v1/rc5/process', data=data, content_type='multipart/form-data')
    assert response.status_code == 400

    response_data = json.loads(response.data.decode('utf-8'))
    assert "Введіть парольну фразу" in response_data['error']


def test_api_rc5_full_cycle(client):
    original_content = b"Data to be encrypted via Flask API."
    password = "api_secret_password"

    encrypt_data = {
        'file': (io.BytesIO(original_content), 'secret.txt'),
        'password': password,
        'key_length': '128',
        'action': 'encrypt'
    }

    encrypt_response = client.post('/api/v1/rc5/process', data=encrypt_data, content_type='multipart/form-data')
    assert encrypt_response.status_code == 200
    assert encrypt_response.mimetype == 'application/octet-stream'

    encrypted_content = encrypt_response.data
    assert encrypted_content != original_content

    decrypt_data = {
        'file': (io.BytesIO(encrypted_content), 'encrypted_secret.txt'),
        'password': password,
        'key_length': '128',
        'action': 'decrypt'
    }

    decrypt_response = client.post('/api/v1/rc5/process', data=decrypt_data, content_type='multipart/form-data')
    assert decrypt_response.status_code == 200
    assert decrypt_response.mimetype == 'application/octet-stream'

    assert decrypt_response.data == original_content


def test_api_rc5_wrong_password(client):
    original_content = b"Some top secret data"

    encrypt_data = {
        'file': (io.BytesIO(original_content), 'data.txt'),
        'password': 'correct_password',
        'action': 'encrypt'
    }
    encrypt_response = client.post('/api/v1/rc5/process', data=encrypt_data, content_type='multipart/form-data')
    encrypted_content = encrypt_response.data

    decrypt_data = {
        'file': (io.BytesIO(encrypted_content), 'data.txt'),
        'password': 'wrong_password',
        'action': 'decrypt'
    }
    decrypt_response = client.post('/api/v1/rc5/process', data=decrypt_data, content_type='multipart/form-data')

    assert decrypt_response.status_code in [400, 500]