import os
from random import randint
import sys
import time
from concurrent.futures import ProcessPoolExecutor
import csv
sys.set_int_max_str_digits(0)

OUTPUT_DIR = './output'
RESULT_FILE = './output/result.csv'


def fib(n: int):
    """Calculate a value in the Fibonacci sequence by ordinal number"""

    f0, f1 = 0, 1
    for _ in range(n-1):
        f0, f1 = f1, f0 + f1
    return f1


def func1(array: list):
    with ProcessPoolExecutor() as executor:
        results = list(executor.map(fib, array))

    for n, val in zip(array, results):
        with open(os.path.join(OUTPUT_DIR, f'{n}.txt'), 'w', encoding='utf-8') as f:
            f.write(str(val))


def func2(result_file: str):
    files = [f for f in os.listdir(OUTPUT_DIR) if f.endswith('.txt')]
    data = []
    for filename in files:
        n = int(filename.split('.')[0])
        with open(os.path.join(OUTPUT_DIR, filename), 'r', encoding='utf-8') as f:
            val = f.read().strip()
        data.append((n, val))

    with open(result_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(data)


if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    func1(array=[randint(1000, 100000) for _ in range(1000)])
    func2(result_file=RESULT_FILE)
