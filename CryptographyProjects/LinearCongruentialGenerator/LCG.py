import math

class LCG:
    def __init__(self, x0=41, m=2**31 - 7, a=2**14, c=75025):
        self.m = m # Модуль
        self.a = a # Множник
        self.c = c # Приріст
        self.x = x0 # Початкове значення
        self.initial_x = x0 # Зберігаємо для пошуку періоду

    def generate(self, n):
        sequence = []
        for _ in range(n):
            self.x = (self.a * self.x + self.c) % self.m 
            sequence.append(self.x)
        return sequence

    @staticmethod
    def gcd(a, b):
        while b > 0:
            a, b = b, a % b
        return a

    def cesaro_test(self, sequence):
        if len(sequence) < 2: return 0
        
        pairs = len(sequence) // 2
        gcd_is_one = 0
        
        for i in range(0, pairs * 2, 2):
            if self.gcd(sequence[i], sequence[i+1]) == 1:
                gcd_is_one += 1
        
        probability = gcd_is_one / pairs
        if probability == 0: return 0
        return math.sqrt(6 / probability)

    def find_period(self, max_iterations=5000000):
        def get_next(val):
            return (self.a * val + self.c) % self.m

        tortoise = get_next(self.initial_x)
        hare = get_next(get_next(self.initial_x))
        steps = 0

        while tortoise != hare:
            tortoise = get_next(tortoise)
            hare = get_next(get_next(hare))
            steps += 1
            if steps > max_iterations:
                return -1

        hare = get_next(tortoise)
        period = 1
        while tortoise != hare:
            hare = get_next(hare)
            period += 1
            if period > max_iterations:
                return -1

        return period
