"""
Write function which receives filename and reads file line by line and returns min and mix integer from file.
Restriction: filename always valid, each line of file contains valid integer value
Examples:
    # file contains following lines:
        10
        -2
        0
        34
    >>> get_min_max('filename')
    (-2, 34)

Hint:
To read file line-by-line you can use this:
with open(filename) as opened_file:
    for line in opened_file:
        ...
"""
from typing import Tuple


def get_min_max(filename: str) -> Tuple[int, int]:
    min_value = float('inf')
    max_value = float('-inf')

    with open(filename) as opened_file:
        for line in opened_file:
            number = int(line)
            min_value = min(number, min_value)
            max_value = max(number, max_value)

    return min_value, max_value


def test_get_min_max():
    assert get_min_max("./practice/1_python_part_1/test_min_max.txt") == (-2, 34)

test_get_min_max()

