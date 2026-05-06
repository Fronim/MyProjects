import unittest
import os
import tempfile
from cryptography.exceptions import InvalidSignature
from DSS.dss_signature import DSSManager


class TestDSSManager(unittest.TestCase):
    def setUp(self):
        self.manager = DSSManager()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.priv_path = os.path.join(self.temp_dir.name, 'private.pem')
        self.pub_path = os.path.join(self.temp_dir.name, 'public.pem')
        self.test_file_path = os.path.join(self.temp_dir.name, 'test_file.txt')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_key_generation(self):
        self.manager.generate_keys(key_size=1024)  # Використовуємо 1024 для швидкості в тестах
        self.assertIsNotNone(self.manager.private_key)
        self.assertIsNotNone(self.manager.public_key)

    def test_save_and_load_keys(self):
        self.manager.generate_keys(key_size=1024)
        self.manager.save_keys_to_files(self.priv_path, self.pub_path)

        self.assertTrue(os.path.exists(self.priv_path))
        self.assertTrue(os.path.exists(self.pub_path))

        new_manager = DSSManager()
        new_manager.load_private_key(self.priv_path)
        new_manager.load_public_key(self.pub_path)

        self.assertIsNotNone(new_manager.private_key)
        self.assertIsNotNone(new_manager.public_key)

    def test_sign_and_verify_text_success(self):
        self.manager.generate_keys(key_size=1024)
        text = "Hello, this is a secret message!"

        signature = self.manager.sign_text(text)
        self.assertTrue(isinstance(signature, str))
        self.assertGreater(len(signature), 0)

        is_valid = self.manager.verify_text(text, signature)
        self.assertTrue(is_valid)

    def test_verify_text_failure_wrong_text(self):
        self.manager.generate_keys(key_size=1024)
        text = "Original text"
        signature = self.manager.sign_text(text)

        is_valid = self.manager.verify_text("Altered text", signature)
        self.assertFalse(is_valid)

    def test_sign_and_verify_file_success(self):
        self.manager.generate_keys(key_size=1024)

        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write("This is a test file content.")

        signature = self.manager.sign_file(self.test_file_path)
        self.assertTrue(isinstance(signature, str))

        is_valid = self.manager.verify_file(self.test_file_path, signature)
        self.assertTrue(is_valid)

    def test_verify_file_failure_altered_file(self):
        self.manager.generate_keys(key_size=1024)

        with open(self.test_file_path, 'w', encoding='utf-8') as f:
            f.write("Original file content.")

        signature = self.manager.sign_file(self.test_file_path)

        with open(self.test_file_path, 'a', encoding='utf-8') as f:
            f.write(" This text was added by a hacker.")

        is_valid = self.manager.verify_file(self.test_file_path, signature)
        self.assertFalse(is_valid)


if __name__ == '__main__':
    unittest.main()