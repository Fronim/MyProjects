import io
import zipfile
import pytest
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_rse_get_page(client):
    response = client.get('/rsa')

    assert response.status_code == 200
    assert b"RSA" in response.data or b"rsa" in response.data.lower()


def test_rse_generate_keys_endpoint(client):
    response = client.post('/rsa', data={
        'action': 'generate_keys',
        'key_size': '1024'
    })

    assert response.status_code == 200
    assert response.mimetype == 'application/zip'

    with zipfile.ZipFile(io.BytesIO(response.data)) as zf:
        files = zf.namelist()
        assert 'private.pem' in files
        assert 'public.pem' in files


def test_rse_full_encryption_flow(client):
    response_keys = client.post('/rsa', data={
        'action': 'generate_keys',
        'key_size': '1024'
    })

    with zipfile.ZipFile(io.BytesIO(response_keys.data)) as zf:
        public_key_bytes = zf.read('public.pem')
        private_key_bytes = zf.read('private.pem')

    original_text = b"This is a highly confidential message for Flask testing!"

    encrypt_data = {
        'action': 'encrypt',
        'file_to_encrypt': (io.BytesIO(original_text), 'secret.txt'),
        'public_key': (io.BytesIO(public_key_bytes), 'public.pem')
    }

    response_encrypt = client.post('/rsa', data=encrypt_data, content_type='multipart/form-data')
    assert response_encrypt.status_code == 200

    encrypted_bytes = response_encrypt.data
    assert encrypted_bytes != original_text
    assert len(encrypted_bytes) > 0

    decrypt_data = {
        'action': 'decrypt',
        'file_to_decrypt': (io.BytesIO(encrypted_bytes), 'secret.txt.encrypted'),
        'private_key': (io.BytesIO(private_key_bytes), 'private.pem')
    }

    response_decrypt = client.post('/rsa', data=decrypt_data, content_type='multipart/form-data')
    assert response_decrypt.status_code == 200

    decrypted_bytes = response_decrypt.data
    assert decrypted_bytes == original_text


def test_rse_missing_file_handling(client):
    encrypt_data = {
        'action': 'encrypt',
        'public_key': (io.BytesIO(b"dummy key data"), 'public.pem')
    }

    response = client.post('/rsa', data=encrypt_data, content_type='multipart/form-data')

    assert response.status_code == 200