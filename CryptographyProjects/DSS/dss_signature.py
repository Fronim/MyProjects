import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import dsa
from cryptography.hazmat.primitives.asymmetric import utils
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature


class DSSManager:

    def __init__(self):
        self.private_key = None
        self.public_key = None

    def generate_keys(self, key_size: int = 2048):
        self.private_key = dsa.generate_private_key(key_size=key_size)
        self.public_key = self.private_key.public_key()

    def save_keys_to_files(self, private_path: str = "private_key.pem", public_path: str = "public_key.pem", password: str = "some_password_123"):
        if not self.private_key or not self.public_key:
            raise ValueError("Keys have not been generated yet!")

        password_bytes = password.encode('utf-8')

        with open(private_path, "wb") as f:
            f.write(
                self.private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.BestAvailableEncryption(password_bytes)
                )
            )

        with open(public_path, "wb") as f:
            f.write(
                self.public_key.public_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PublicFormat.SubjectPublicKeyInfo
                )
            )

    def load_private_key(self, private_path: str, password: str = "secret_pass_123"):
        password_bytes = password.encode('utf-8')
        with open(private_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(f.read(), password=password_bytes)

    def load_public_key(self, public_path: str):
        with open(public_path, "rb") as f:
            self.public_key = serialization.load_pem_public_key(f.read())


    def sign_text(self, text: str) -> str:
        if not self.private_key:
            raise ValueError("Private key are not set!")

        data = text.encode('utf-8')
        signature = self.private_key.sign(
            data,
            hashes.SHA256()
        )
        return signature.hex()

    def verify_text(self, text: str, signature_hex: str) -> bool:
        if not self.public_key:
            raise ValueError("Public key are not set!")

        data = text.encode('utf-8')
        try:
            signature_bytes = bytes.fromhex(signature_hex)
            self.public_key.verify(
                signature_bytes,
                data,
                hashes.SHA256()
            )
            return True
        except (InvalidSignature, ValueError):
            return False


    def sign_file(self, file_path: str) -> str:
        if not self.private_key:
            raise ValueError("Private key are not set!")

        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)

        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)

        digest = hasher.finalize()
        signature = self.private_key.sign(
            digest,
            utils.Prehashed(chosen_hash)
        )
        return signature.hex()

    def verify_file(self, file_path: str, signature_hex: str) -> bool:
        if not self.public_key:
            raise ValueError("Public key are not set!")

        chosen_hash = hashes.SHA256()
        hasher = hashes.Hash(chosen_hash)

        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)

            digest = hasher.finalize()
            signature_bytes = bytes.fromhex(signature_hex)

            self.public_key.verify(
                signature_bytes,
                digest,
                utils.Prehashed(chosen_hash)
            )
            return True
        except (InvalidSignature, ValueError, FileNotFoundError):
            return False