"""
Write tests for division() function in 2_python_part_2/task_exceptions.py
In case (1,1) it should check if exception were raised
In case (1,0) it should check if return value is None and "Division by 0" printed
If other cases it should check if division is correct

TIP: to test output of print() function use capfd fixture
https://stackoverflow.com/a/20507769
"""
import pytest 
module = __import__('2_python_part_2.task_exceptions', fromlist=['DivideByOneError', 'division'])
DivideByOneError = module.DivideByOneError
division = module.division

def test_division_ok(capfd):
    assert division(6, 2) == 3
    out, err = capfd.readouterr()
    assert out == 'Division finished\n'


def test_division_by_zero(capfd):
    assert division(3, 0) == None
    out, err = capfd.readouterr()
    assert out == 'Division by 0\nDivision finished\n'


def test_division_by_one(capfd):
    with pytest.raises(DivideByOneError) as e:
        division(10, 1)
    out, err = capfd.readouterr()
    assert 'Deletion on 1 get the same result' in str(e.value)
    assert out == 'Division finished\n'