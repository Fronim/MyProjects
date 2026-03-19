import struct
import os

class MyMD5:
    def __init__(self, A=0x67452301, B=0xEFCDAB89, C=0x98BADCFE, D=0x10325476, rotate_list = [0], constant_add = [0]):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.r = rotate_list
        self.k = constant_add
        if len(rotate_list) != 64:
            self.r = [7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22,  7, 12, 17, 22, 5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20,  5,  9, 14, 20, 4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23,  4, 11, 16, 23, 6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21,  6, 10, 15, 21]
        if len(constant_add) != 64:
            self.k = [ 0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee, 0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501, 0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa, 0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8, 0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed, 0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a, 0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c, 0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70, 0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05, 0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665, 0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039, 0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1, 0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1, 0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391]

    def reset(self, A=0x67452301, B=0xEFCDAB89, C=0x98BADCFE, D=0x10325476):
        self.A = A
        self.B = B
        self.C = C
        self.D = D

    def data_to_list(self, data):
        if isinstance(data, str):
            data = data.encode('utf-8')

        original_length_in_bits = len(data) * 8

        data += b'\x80'

        while len(data) % 64 != 56: # 8 * 56 = 448
            data += b'\x00'

        data += struct.pack('<Q', original_length_in_bits)


        for i in range(0, len(data), 64): # збираєм блоки по 64 байтів де розбиваєм його на 16 "слів" які складаються з 4 байтів кожен
            chunk = data[i: i + 64]
            words = list(struct.unpack('<16I', chunk))
            yield words

    def file_to_list(self, filepath):
        file_size_bytes = os.path.getsize(filepath)
        original_length_in_bits = file_size_bytes * 8

        with open(filepath, 'rb') as f:
            while True:
                chunk = f.read(64)

                if len(chunk) == 64:
                    yield list(struct.unpack('<16I', chunk))
                else:
                    data = bytearray(chunk)
                    data.append(0x80)

                    while len(data) % 64 != 56:
                        data.append(0x00)

                    data += struct.pack('<Q', original_length_in_bits)

                    for i in range(0, len(data), 64):
                        final_chunk = data[i: i + 64]
                        yield list(struct.unpack('<16I', final_chunk))

                    break

    def F(self, B, C, D, general_count):
        if 0 <= general_count <= 15:
            return (B & C) | ((~B & 0xFFFFFFFF) & D)
        elif 16 <= general_count <= 31:
            return (D & B) | ((~D & 0xFFFFFFFF) & C)
        elif 32 <= general_count <= 47:
            return B ^ C ^ D
        elif 48 <= general_count <= 63:
            return C ^ (B | (~D & 0xFFFFFFFF))

    def combine (self, general_count, input_word):
        A, B, C, D, = self.A, self.B, self.C, self.D
        temp = (A + self.F(B, C, D, general_count)) & 0xFFFFFFFF
        return (temp + input_word) & 0xFFFFFFFF

    @staticmethod
    def rotate(num, rotate_count):
        num &= 0xFFFFFFFF
        rotate_count %= 32
        new_num = num << rotate_count
        wrap = num >> (32 - rotate_count)
        return (new_num | wrap) & 0xFFFFFFFF

    def constant_change(self, comb, general_count):
        return (self.rotate((comb + self.k[general_count]), self.r[general_count]) + self.B) & 0xFFFFFFFF

    def full_step(self, general_count, input_word):
        new_A = self.D
        new_B = self.constant_change(self.combine(general_count, input_word), general_count)
        new_C = self.B
        new_D = self.C

        return new_A, new_B, new_C, new_D

    def hash(self, data):
        self.reset()
        four_iter = [lambda x: (x % 16), lambda x: ((5 * x + 1) % 16), lambda x: ((3 * x + 5) % 16),lambda x: ((7 * x) % 16)]
        for words in self.data_to_list(data):
            AA, BB, CC, DD = self.A, self.B, self.C, self.D
            general_count = 0

            for i in range(4):
                for j in range(16):
                    cur_word = words[four_iter[i](j)]
                    self.A, self.B, self.C, self.D = self.full_step(general_count, cur_word)
                    general_count += 1

        self.A = (self.A + AA) & 0xFFFFFFFF
        self.B = (self.B + BB) & 0xFFFFFFFF
        self.C = (self.C + CC) & 0xFFFFFFFF
        self.D = (self.D + DD) & 0xFFFFFFFF

    def hash_file(self, filepath):
        self.reset()
        four_iter = [
            lambda x: (x % 16),
            lambda x: ((5 * x + 1) % 16),
            lambda x: ((3 * x + 5) % 16),
            lambda x: ((7 * x) % 16)
        ]

        for words in self.file_to_list(filepath):
            AA, BB, CC, DD = self.A, self.B, self.C, self.D
            general_count = 0

            for i in range(4):
                for j in range(16):
                    cur_word = words[four_iter[i](j)]
                    self.A, self.B, self.C, self.D = self.full_step(general_count, cur_word)
                    general_count += 1

            self.A = (self.A + AA) & 0xFFFFFFFF
            self.B = (self.B + BB) & 0xFFFFFFFF
            self.C = (self.C + CC) & 0xFFFFFFFF
            self.D = (self.D + DD) & 0xFFFFFFFF


        final_bytes = struct.pack('<4I', self.A, self.B, self.C, self.D)
        return final_bytes.hex()