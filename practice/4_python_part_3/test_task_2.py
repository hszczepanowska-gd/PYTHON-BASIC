import math
import pytest

from task_2 import math_calculate, OperationNotFoundException

def test_math_calculate_log_function():
    assert math_calculate("log", 1024, 2) == 10.0


def test_math_calculate_ceil_function():
    assert math_calculate("ceil", 10.7) == 11


def test_math_calculate_nonexistent_operation_raises():
    with pytest.raises(OperationNotFoundException):
        math_calculate("non_existing_op", 1)


def test_math_calculate_with_too_many_args():
    with pytest.raises(TypeError):
        math_calculate("ceil", 1, 2, 3)


def test_math_calculate_with_zero_args():
    with pytest.raises(TypeError):
        math_calculate("ceil")


