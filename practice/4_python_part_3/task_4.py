"""
Create virtual environment and install Faker package only for this venv.
Write command line tool which will receive int as a first argument and one or more named arguments
 and generates defined number of dicts separated by new line.
Exec format:
`$python task_4.py NUMBER --FIELD=PROVIDER [--FIELD=PROVIDER...]`
where:
NUMBER - positive number of generated instances
FIELD - key used in generated dict
PROVIDER - name of Faker provider
Example:
`$python task_4.py 2 --fake-address=address --some_name=name`
{"some_name": "Chad Baird", "fake-address": "62323 Hobbs Green\nMaryshire, WY 48636"}
{"some_name": "Courtney Duncan", "fake-address": "8107 Nicole Orchard Suite 762\nJosephchester, WI 05981"}
"""

import argparse
from faker import Faker

def parse_arguments(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate fake data using Faker")
    parser.add_argument("NUMBER", type=int, help="How many fake records to generate.")
    ns, rest = parser.parse_known_args(argv)

    fields = {}
    for field in rest:
        if field.startswith("--") and "=" in field:
            key, value = field[2:].split("=", 1)
            key, value = key.strip(), value.strip()
            if key and value:
                fields[key] = value

    ns.fields = fields
    return ns

def print_name_address(args: argparse.Namespace) -> None:
    fake = Faker()
    for _ in range(args.NUMBER):
        row = {}
        for field, provider in args.fields.items():
            data = getattr(fake, provider)()
            row[field] = data

        print(row)

def main(argv=None):
    args = parse_arguments(argv)
    print_name_address(args)


if __name__ == "__main__":
    main()

"""
Write test for print_name_address function
Use Mock for mocking args argument https://docs.python.org/3/library/unittest.mock.html#unittest.mock.Mock
Example:
    >>> m = Mock()
    >>> m.method.return_value = 123
    >>> m.method()
    123
"""
