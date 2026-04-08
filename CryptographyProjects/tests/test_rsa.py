import os
import pytest
from cryptography.exceptions import InvalidSignature
from RSAEncryption.RSA import RSACipher


@pytest.fixture
def temp_files(tmp_path):
    return {
        'private_key': tmp_path / "private.pem",
        'public_key': tmp_path / "public.pem",
        'plaintext': tmp_path / "plaintext.txt",
        'encrypted': tmp_path / "encrypted.bin",
        'decrypted': tmp_path / "decrypted.txt"
    }


def test_key_generation():
    cipher = RSACipher(key_size=1024)

    assert cipher.private_key is None
    assert cipher.public_key is None

    cipher.generate_keys()

    assert cipher.private_key is not None
    assert cipher.public_key is not None


def test_save_and_load_keys(temp_files):
    cipher = RSACipher(key_size=1024)
    cipher.generate_keys()

    priv_path = str(temp_files['private_key'])
    pub_path = str(temp_files['public_key'])

    # Зберігаємо ключі
    cipher.save_keys(priv_path, pub_path)

    assert os.path.exists(priv_path)
    assert os.path.exists(pub_path)

    new_cipher = RSACipher()
    new_cipher.load_keys(priv_path, pub_path)

    assert new_cipher.private_key is not None
    assert new_cipher.public_key is not None


def test_save_and_load_keys_with_password(temp_files):
    cipher = RSACipher(key_size=1024)
    cipher.generate_keys()

    priv_path = str(temp_files['private_key'])
    pub_path = str(temp_files['public_key'])
    password = "secure_password_123"

    cipher.save_keys(priv_path, pub_path, password=password)

    new_cipher = RSACipher()
    new_cipher.load_keys(priv_path, pub_path, password=password)

    assert new_cipher.private_key is not None
    assert new_cipher.public_key is not None


def test_encrypt_decrypt_file_integrity(temp_files):
    cipher = RSACipher(key_size=1024)
    cipher.generate_keys()

    plain_path = str(temp_files['plaintext'])
    enc_path = str(temp_files['encrypted'])
    dec_path = str(temp_files['decrypted'])

    original_data = b"A" * 150 + b"B" * 150 + b"12345"

    with open(plain_path, 'wb') as f:
        f.write(original_data)

    cipher.encrypt_file(plain_path, enc_path)
    assert os.path.exists(enc_path)
    assert os.path.getsize(enc_path) > 0

    cipher.decrypt_file(enc_path, dec_path)
    assert os.path.exists(dec_path)

    with open(dec_path, 'rb') as f:
        decrypted_data = f.read()

    assert original_data == decrypted_data


def test_individual_key_loading(temp_files):
    cipher = RSACipher(key_size=1024)
    cipher.generate_keys()

    priv_path = str(temp_files['private_key'])
    pub_path = str(temp_files['public_key'])
    cipher.save_keys(priv_path, pub_path)

    cipher_pub = RSACipher()
    cipher_pub.load_public_key(pub_path)
    assert cipher_pub.public_key is not None
    assert cipher_pub.private_key is None

    cipher_priv = RSACipher()
    cipher_priv.load_private_key(priv_path)
    assert cipher_priv.private_key is not None
    assert cipher_priv.public_key is None


def test_encrypt_without_public_key_raises_error(temp_files):
    cipher = RSACipher()
    plain_path = str(temp_files['plaintext'])
    enc_path = str(temp_files['encrypted'])

    with open(plain_path, 'wb') as f:
        f.write(b"Test data")

    with pytest.raises(ValueError, match="Публічний ключ не завантажено!"):
        cipher.encrypt_file(plain_path, enc_path)


def test_decrypt_without_private_key_raises_error(temp_files):
    cipher = RSACipher()
    enc_path = str(temp_files['encrypted'])
    dec_path = str(temp_files['decrypted'])

    with open(enc_path, 'wb') as f:
        f.write(b"Test data")

    with pytest.raises(ValueError, match="Приватний ключ не завантажено!"):
        cipher.decrypt_file(enc_path, dec_path)