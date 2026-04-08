import os
import struct
import time
from MD5Hash.MD5 import MyMD5
from LinearCongruentialGenerator.LCG import LCG


def pad(data: bytes, block_size: int) -> bytes:
    padding_len = block_size - (len(data) % block_size)
    return data + bytes([padding_len] * padding_len)


def unpad(data: bytes, block_size: int) -> bytes:
    if not data:
        return data

    padding_len = data[-1]

    if padding_len < 1 or padding_len > block_size:
        raise ValueError("Неправильний пароль або файл пошкоджено (помилка паддінгу)")

    expected_padding = bytes([padding_len] * padding_len)
    if data[-padding_len:] != expected_padding:
        raise ValueError("Неправильний пароль або файл пошкоджено (помилка паддінгу)")

    return data[:-padding_len]


def xor_bytes(b1: bytes, b2: bytes) -> bytes:
    return bytes(x ^ y for x, y in zip(b1, b2))


class RC5:

    def __init__(self, key: bytes, w: int = 32, r: int = 12):
        self.w = w
        self.r = r
        self.key = key
        self.b = len(key)
        self.u = w // 8
        self.c = max(1, (self.b + self.u - 1) // self.u)
        self.S = []

        if w == 32:
            self.P = 0xB7E15163
            self.Q = 0x9E3779B9
        else:
            raise ValueError("Ця реалізація оптимізована для w=32")

        self.mod = 1 << self.w
        self._key_expansion()

    def _rol(self, val: int, shift: int) -> int:
        shift %= self.w
        return ((val << shift) | (val >> (self.w - shift))) & (self.mod - 1)

    def _ror(self, val: int, shift: int) -> int:
        shift %= self.w
        return ((val >> shift) | (val << (self.w - shift))) & (self.mod - 1)

    def _key_expansion(self):
        L = [0] * self.c
        for i in range(self.b):
            L[i // self.u] = (L[i // self.u] + (self.key[i] << (8 * (i % self.u)))) & (self.mod - 1)

        self.S = [0] * (2 * self.r + 2)
        self.S[0] = self.P
        for i in range(1, len(self.S)):
            self.S[i] = (self.S[i - 1] + self.Q) & (self.mod - 1)

        i = j = 0
        A = B = 0
        t = 2 * self.r + 2
        iterations = 3 * max(t, self.c)

        for _ in range(iterations):
            A = self.S[i] = self._rol((self.S[i] + A + B) & (self.mod - 1), 3)
            B = L[j] = self._rol((L[j] + A + B) & (self.mod - 1), A + B)
            i = (i + 1) % t
            j = (j + 1) % self.c

    def encrypt_block(self, data: bytes) -> bytes:
        A = int.from_bytes(data[:self.u], byteorder='little')
        B = int.from_bytes(data[self.u:], byteorder='little')

        A = (A + self.S[0]) & (self.mod - 1)
        B = (B + self.S[1]) & (self.mod - 1)

        for i in range(1, self.r + 1):
            A = (self._rol(A ^ B, B) + self.S[2 * i]) & (self.mod - 1)
            B = (self._rol(B ^ A, A) + self.S[2 * i + 1]) & (self.mod - 1)

        return A.to_bytes(self.u, byteorder='little') + B.to_bytes(self.u, byteorder='little')

    def decrypt_block(self, data: bytes) -> bytes:
        A = int.from_bytes(data[:self.u], byteorder='little')
        B = int.from_bytes(data[self.u:], byteorder='little')

        for i in range(self.r, 0, -1):
            B = self._ror((B - self.S[2 * i + 1]) & (self.mod - 1), A) ^ A
            A = self._ror((A - self.S[2 * i]) & (self.mod - 1), B) ^ B

        B = (B - self.S[1]) & (self.mod - 1)
        A = (A - self.S[0]) & (self.mod - 1)

        return A.to_bytes(self.u, byteorder='little') + B.to_bytes(self.u, byteorder='little')


class RC5FileProcessor:

    def __init__(self, password: str, key_length_bits: int = 128, w: int = 32, r: int = 12):
        self.key = self._derive_key(password, key_length_bits)
        self.rc5 = RC5(self.key, w, r)
        self.block_size = (w // 8) * 2

    def _derive_key(self, password: str, key_length_bits: int) -> bytes:
        md5 = MyMD5()
        md5.hash(password.encode('utf-8'))
        hash_p = struct.pack('<4I', md5.A, md5.B, md5.C, md5.D)

        if key_length_bits == 64:
            return hash_p[:8]
        elif key_length_bits == 128:
            return hash_p
        elif key_length_bits == 256:
            md5_2 = MyMD5()
            md5_2.hash(hash_p)
            hash_h_p = struct.pack('<4I', md5_2.A, md5_2.B, md5_2.C, md5_2.D)
            return hash_h_p + hash_p
        else:
            raise ValueError("Непідтримувана довжина ключа")

    def encrypt_file(self, input_filepath: str, output_filepath: str):
        seed = int(time.time() * 1000) % (2 ** 31 - 7)
        lcg = LCG(x0=seed)

        iv_words = lcg.generate(self.block_size // 4)
        iv = struct.pack(f'<{len(iv_words)}I', *iv_words)[:self.block_size]

        encrypted_iv = self.rc5.encrypt_block(iv)

        with open(input_filepath, 'rb') as f_in, open(output_filepath, 'wb') as f_out:
            f_out.write(encrypted_iv)

            prev_block = iv
            while True:
                chunk = f_in.read(self.block_size)

                if len(chunk) < self.block_size:
                    padded_chunk = pad(chunk, self.block_size)
                    ct_block = self.rc5.encrypt_block(xor_bytes(padded_chunk, prev_block))
                    f_out.write(ct_block)
                    break
                else:
                    ct_block = self.rc5.encrypt_block(xor_bytes(chunk, prev_block))
                    f_out.write(ct_block)
                    prev_block = ct_block

    def decrypt_file(self, input_filepath: str, output_filepath: str):
        with open(input_filepath, 'rb') as f_in, open(output_filepath, 'wb') as f_out:
            encrypted_iv = f_in.read(self.block_size)
            if len(encrypted_iv) < self.block_size:
                raise ValueError("Файл занадто малий або пошкоджений")

            iv = self.rc5.decrypt_block(encrypted_iv)
            prev_block = iv

            prev_decrypted_chunk = b""

            while True:
                chunk = f_in.read(self.block_size)
                if not chunk:
                    break

                pt_block = xor_bytes(self.rc5.decrypt_block(chunk), prev_block)
                prev_block = chunk

                if prev_decrypted_chunk:
                    f_out.write(prev_decrypted_chunk)

                prev_decrypted_chunk = pt_block

            if prev_decrypted_chunk:
                unpadded = unpad(prev_decrypted_chunk, self.block_size)
                f_out.write(unpadded)