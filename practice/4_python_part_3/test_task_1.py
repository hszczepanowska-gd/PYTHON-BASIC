import pytest
from freezegun import freeze_time
from task_1 import calculate_days, WrongFormatException


@freeze_time("2025-09-16")  
@pytest.mark.parametrize(
    "given_date, expected_result",
    [
        ("2025-09-16", 0),
        ("2025-09-15", 1),
        ("2025-09-17", -1),
    ],
)
def test_calculate_days(given_date, expected_result):
    assert calculate_days(given_date) == expected_result

def test_calculate_days_raises_on_wrong_format_examples():
    with pytest.raises(WrongFormatException):
        calculate_days("16-09-2025")
    with pytest.raises(WrongFormatException):
        calculate_days("2025/09/16")
