import os
import pytest
from RC5Encryption.RC5 import RC5, RC5FileProcessor, pad, unpad


def test_padding():
    data = b"hello"
    block_size = 8
    padded = pad(data, block_size)

    assert len(padded) % block_size == 0
    assert padded == b"hello\x03\x03\x03"
    # Додано block_size як другий аргумент
    assert unpad(padded, block_size) == data


def test_padding_full_block():
    data = b"12345678"
    block_size = 8
    padded = pad(data, block_size)

    assert len(padded) == 16
    assert padded == b"12345678\x08\x08\x08\x08\x08\x08\x08\x08"
    # Додано block_size як другий аргумент
    assert unpad(padded, block_size) == data


def test_rc5_block_encryption():
    key = b"secretkey1234567"  # 16 байтів = 128 бітів
    rc5 = RC5(key)
    plaintext = b"abcdefgh"  # 8 байтів = 64 біти (оскільки w=32)

    ciphertext = rc5.encrypt_block(plaintext)
    assert ciphertext != plaintext

    decrypted = rc5.decrypt_block(ciphertext)
    assert decrypted == plaintext


def test_key_derivation_lengths():
    password = "test_password"

    proc_64 = RC5FileProcessor(password, key_length_bits=64)
    assert len(proc_64.key) == 8  # 8 байтів = 64 біти

    proc_128 = RC5FileProcessor(password, key_length_bits=128)
    assert len(proc_128.key) == 16  # 16 байтів = 128 бітів

    proc_256 = RC5FileProcessor(password, key_length_bits=256)
    assert len(proc_256.key) == 32  # 32 байти = 256 бітів


def test_rc5_file_processing_cycle(tmp_path):
    password = "secure_test_password"
    processor = RC5FileProcessor(password, key_length_bits=128)

    input_file = tmp_path / "original.txt"
    encrypted_file = tmp_path / "encrypted.bin"
    decrypted_file = tmp_path / "decrypted.txt"

    original_data = b"This is a test message. It doesn't align perfectly with block sizes!"
    input_file.write_bytes(original_data)

    processor.encrypt_file(str(input_file), str(encrypted_file))
    assert encrypted_file.exists()
    assert encrypted_file.stat().st_size > len(original_data)  # Розмір має збільшитись через IV та паддінг

    processor.decrypt_file(str(encrypted_file), str(decrypted_file))
    assert decrypted_file.read_bytes() == original_data