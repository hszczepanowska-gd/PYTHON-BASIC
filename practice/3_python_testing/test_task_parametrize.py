"""
Write a parametrized test for two functions.
The functions are used to find a number by ordinal in the Fibonacci sequence.
One of them has a bug.

Fibonacci sequence: https://en.wikipedia.org/wiki/Fibonacci_number

Task:
 1. Write a test with @pytest.mark.parametrize decorator.
 2. Find the buggy function and fix it.
"""
import pytest

def fibonacci_1(n):
    a, b = 0, 1
    for _ in range(n-1):
        a, b = b, a + b
    return b


def fibonacci_2(n):
    fibo = [0, 1]
    for i in range(1, n+1):
        fibo.append(fibo[i-1] + fibo[i])
    return fibo[n]

test_params = [
    (1,1),
    (2,1),
    (3,2),
    (4,3),
    (5,5),
    (6,8),
    (7,13),
]

@pytest.mark.parametrize('n, expected_result', test_params)
def test_fibonacci_1(n, expected_result):
    assert expected_result == fibonacci_1(n)

@pytest.mark.parametrize('n, expected_result', test_params)
def test_fibonacci_2(n, expected_result):
    assert expected_result == fibonacci_2(n)