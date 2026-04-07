import os
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend


class RSACipher:

    def __init__(self, key_size=2048):
        self.key_size = key_size
        self.private_key = None
        self.public_key = None

        hash_size = hashes.SHA256().digest_size
        self.cipher_chunk_size = self.key_size // 8
        self.plain_chunk_size = self.cipher_chunk_size - 2 * hash_size - 2

    def generate_keys(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.key_size,
            backend=default_backend()
        )
        self.public_key = self.private_key.public_key()

    def save_keys(self, private_path, public_path, password=None):
        if not self.private_key or not self.public_key:
            raise ValueError("Ключі ще не згенеровані!")

        if password:
            if isinstance(password, str):
                password = password.encode()
            encryption_alg = serialization.BestAvailableEncryption(password)
        else:
            encryption_alg = serialization.NoEncryption()

        pem_private = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption_alg
        )
        with open(private_path, 'wb') as f:
            f.write(pem_private)

        pem_public = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(public_path, 'wb') as f:
            f.write(pem_public)

    def load_keys(self, private_path, public_path, password=None):
        if password and isinstance(password, str):
            password = password.encode()

        with open(private_path, 'rb') as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(),
                password=password,
                backend=default_backend()
            )

        with open(public_path, 'rb') as f:
            self.public_key = serialization.load_pem_public_key(
                f.read(),
                backend=default_backend()
            )

    def encrypt_file(self, input_path, output_path):
        if not self.public_key:
            raise ValueError("Публічний ключ не завантажено!")

        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(self.plain_chunk_size)
                if not chunk:
                    break

                encrypted_chunk = self.public_key.encrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                f_out.write(encrypted_chunk)

    def decrypt_file(self, input_path, output_path):
        if not self.private_key:
            raise ValueError("Приватний ключ не завантажено!")

        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(self.cipher_chunk_size)
                if not chunk:
                    break

                decrypted_chunk = self.private_key.decrypt(
                    chunk,
                    padding.OAEP(
                        mgf=padding.MGF1(algorithm=hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )
                f_out.write(decrypted_chunk)