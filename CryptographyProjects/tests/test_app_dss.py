import unittest
import os
import io
import tempfile
import zipfile
from app import app
from DSS.dss_signature import DSSManager

class TestFlaskRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
        self.temp_dir = tempfile.TemporaryDirectory()

        self.manager = DSSManager()
        self.manager.generate_keys(key_size=1024)

        self.priv_path = os.path.join(self.temp_dir.name, 'private.pem')
        self.pub_path = os.path.join(self.temp_dir.name, 'public.pem')
        self.manager.save_keys_to_files(self.priv_path, self.pub_path)

        with open(self.priv_path, 'rb') as f:
            self.priv_bytes = f.read()
        with open(self.pub_path, 'rb') as f:
            self.pub_bytes = f.read()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dss_get_route(self):
        response = self.client.get('/dss')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'DSS Digital Signature', response.data)

    def test_dss_generate_keys(self):
        data = {
            'action': 'generate_keys',
            'key_size': '1024'
        }
        response = self.client.post('/dss', data=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/zip')

        with zipfile.ZipFile(io.BytesIO(response.data)) as zf:
            files = zf.namelist()
            self.assertIn('private_key.pem', files)
            self.assertIn('public_key.pem', files)

    def test_dss_sign_text(self):
        data = {
            'action': 'sign_text',
            'text_to_sign': 'Test string for Flask',
            'private_key': (io.BytesIO(self.priv_bytes), 'private_key.pem')
        }
        response = self.client.post(
            '/dss',
            data=data,
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Текст успішно підписано!'.encode('utf-8'), response.data)
        self.assertIn(b'Generated Signature (HEX):', response.data)

    def test_dss_verify_text(self):
        text = "Data to verify"
        signature_hex = self.manager.sign_text(text)

        data = {
            'action': 'verify_text',
            'text_to_verify': text,
            'signature_hex': signature_hex,
            'public_key': (io.BytesIO(self.pub_bytes), 'public_key.pem')
        }
        response = self.client.post(
            '/dss',
            data=data,
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Підпис дійсний'.encode('utf-8'), response.data)

    def test_dss_sign_file(self):
        file_content = b"Content of the uploaded file."
        data = {
            'action': 'sign_file',
            'file_to_sign': (io.BytesIO(file_content), 'test.txt'),
            'private_key': (io.BytesIO(self.priv_bytes), 'private_key.pem')
        }
        response = self.client.post(
            '/dss',
            data=data,
            content_type='multipart/form-data'
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('успішно підписано!'.encode('utf-8'), response.data)


if __name__ == '__main__':
    unittest.main()