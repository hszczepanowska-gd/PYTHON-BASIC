"""
Write tests for a read_numbers function.
It should check successful and failed cases
for example:
Test if user inputs: 1, 2, 3, 4
Test if user inputs: 1, 2, Text

Tip: for passing custom values to the input() function
Use unittest.mock patch function
https://docs.python.org/3/library/unittest.mock.html#unittest.mock.patch

TIP: for testing builtin input() function create another function which return input() and mock returned value
"""
from unittest.mock import patch
module = __import__('2_python_part_2.task_input_output', fromlist=['read_numbers'])
read_numbers = module.read_numbers

@patch("builtins.input", side_effect=['1', '2', '3', '4'])
def test_read_numbers_without_text_input(mocked_input):
    result = read_numbers(4)
    assert result == 'Avg: 2.50'


@patch("builtins.input", side_effect=['1', '2', 'Text', '3'])
def test_read_numbers_with_text_input(mocked_input):
    result = read_numbers(4)
    assert result == 'Avg: 2.00'
