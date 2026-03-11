import pytest
import math
from LinearCongruentialGenerator.LCG import LCG

def test_lcg_deterministic_output():
    m, a, c, x0 = 100, 3, 1, 10
    gen1 = LCG(m, a, c, x0)
    gen2 = LCG(m, a, c, x0)
    assert gen1.generate(5) == gen2.generate(5)

def test_gcd_calculation():
    assert LCG.gcd(48, 18) == 6
    assert LCG.gcd(17, 13) == 1

def test_cesaro_pi_estimate():
    gen = LCG()
    sequence = [3, 5, 7, 11]
    estimate = gen.cesaro_test(sequence)
    assert math.isclose(estimate, math.sqrt(6), rel_tol=1e-5)


def test_find_period_success():
    m, a, c, x0 = 100, 3, 1, 10
    gen = LCG(x0=x0, m=m, a=a, c=c)

    period = gen.find_period()
    assert period == 20


def test_find_period_exceeds_max_iterations():
    m, a, c, x0 = 100, 3, 1, 10
    gen = LCG(x0=x0, m=m, a=a, c=c)
    period = gen.find_period(max_iterations=5)
    assert period == -1