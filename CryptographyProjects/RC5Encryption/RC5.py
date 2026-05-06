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
        self.s_table = []

        if w == 32:
            self.p_const = 0xB7E15163
            self.q_const = 0x9E3779B9
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
        l_table = [0] * self.c
        for i in range(self.b):
            l_table[i // self.u] = (l_table[i // self.u] + (self.key[i] << (8 * (i % self.u)))) & (self.mod - 1)

        self.s_table = [0] * (2 * self.r + 2)
        self.s_table[0] = self.p_const
        for i in range(1, len(self.s_table)):
            self.s_table[i] = (self.s_table[i - 1] + self.q_const) & (self.mod - 1)

        i = j = 0
        a_val = b_val = 0
        t_val = 2 * self.r + 2
        iterations = 3 * max(t_val, self.c)

        for _ in range(iterations):
            a_val = self.s_table[i] = self._rol((self.s_table[i] + a_val + b_val) & (self.mod - 1), 3)
            b_val = l_table[j] = self._rol((l_table[j] + a_val + b_val) & (self.mod - 1), a_val + b_val)
            i = (i + 1) % t_val
            j = (j + 1) % self.c

    def encrypt_block(self, data: bytes) -> bytes:
        a_val = int.from_bytes(data[:self.u], byteorder='little')
        b_val = int.from_bytes(data[self.u:], byteorder='little')

        a_val = (a_val + self.s_table[0]) & (self.mod - 1)
        b_val = (b_val + self.s_table[1]) & (self.mod - 1)

        for i in range(1, self.r + 1):
            a_val = (self._rol(a_val ^ b_val, b_val) + self.s_table[2 * i]) & (self.mod - 1)
            b_val = (self._rol(b_val ^ a_val, a_val) + self.s_table[2 * i + 1]) & (self.mod - 1)

        return a_val.to_bytes(self.u, byteorder='little') + b_val.to_bytes(self.u, byteorder='little')

    def decrypt_block(self, data: bytes) -> bytes:
        a_val = int.from_bytes(data[:self.u], byteorder='little')
        b_val = int.from_bytes(data[self.u:], byteorder='little')

        for i in range(self.r, 0, -1):
            b_val = self._ror((b_val - self.s_table[2 * i + 1]) & (self.mod - 1), a_val) ^ a_val
            a_val = self._ror((a_val - self.s_table[2 * i]) & (self.mod - 1), b_val) ^ b_val

        b_val = (b_val - self.s_table[1]) & (self.mod - 1)
        a_val = (a_val - self.s_table[0]) & (self.mod - 1)

        return a_val.to_bytes(self.u, byteorder='little') + b_val.to_bytes(self.u, byteorder='little')


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
            md5_2 = MyMD5()  # NOSONAR
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