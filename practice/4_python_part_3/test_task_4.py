import ast
from unittest.mock import Mock
import pytest

from task_4 import print_name_address


def test_print_name_address(capfd):
    args = Mock()
    args.NUMBER = 2
    args.fields = {
        "some_name": "name",
        "fake-address": "address",
    }

    print_name_address(args)
    out = capfd.readouterr().out.strip()
    lines = out.splitlines()
    assert len(lines) == 2

    for line in lines:
        obj = ast.literal_eval(line)
        assert set(obj.keys()) == {"some_name", "fake-address"}
        assert isinstance(obj["some_name"], str) and obj["some_name"]
        assert isinstance(obj["fake-address"], str) and obj["fake-address"]


def test_print_name_address_when_no_fields(capfd):
    args = Mock()
    args.NUMBER = 3
    args.fields = {}

    print_name_address(args)
    out = capfd.readouterr().out.strip()
    lines = out.splitlines()

    assert len(lines) == 3
    for line in lines:
        assert line.strip() == "{}"


def test_print_name_address_unknown_provider_raises_attribute_error():
    args = Mock()
    args.NUMBER = 1
    args.fields = {"bad": "not_a_real_provider"}

    with pytest.raises(AttributeError):
        print_name_address(args)
