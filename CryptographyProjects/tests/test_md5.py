import pytest
import hashlib
from MD5Hash.MD5 import MyMD5


@pytest.fixture
def md5():
    return MyMD5()

def test_rotate_left(md5):
    assert md5.rotate(1, 1) == 2

    assert md5.rotate(0x80000000, 1) == 1

    assert md5.rotate(0xFFFFFFFF, 17) == 0xFFFFFFFF

    assert md5.rotate(1, 33) == 2


def test_f_function_logic(md5):
    B, C, D = 0x0000FFFF, 0x0F0F0F0F, 0x33333333

    expected_step_1 = 0x33330F0F
    assert md5.F(B, C, D, 5) == expected_step_1

    expected_step_2 = 0x0C0C3F3F
    assert md5.F(B, C, D, 20) == expected_step_2



TEST_STRINGS = [
    b"",
    b"a",
    b"abc",
    b"message digest",
    b"abcdefghijklmnopqrstuvwxyz",
    b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
    b"1234567890" * 8,
    pytest.param(b"a" * 100000, id="large_100k_file")
]

@pytest.mark.parametrize("test_data", TEST_STRINGS)
def test_hash_file_matches_hashlib(md5, tmp_path, test_data):
    temp_file = tmp_path / "test_input.bin"
    temp_file.write_bytes(test_data)

    expected_hash = hashlib.md5(test_data).hexdigest()
    custom_hash = md5.hash_file(str(temp_file))

    assert custom_hash == expected_hash, f"Failed on input length: {len(test_data)}"


def test_state_reset_between_hashes(md5, tmp_path):
    file1 = tmp_path / "file1.txt"
    file1.write_bytes(b"hello")

    file2 = tmp_path / "file2.txt"
    file2.write_bytes(b"world")

    hash1 = md5.hash_file(str(file1))
    assert hash1 == hashlib.md5(b"hello").hexdigest()

    hash2 = md5.hash_file(str(file2))
    assert hash2 == hashlib.md5(b"world").hexdigest()