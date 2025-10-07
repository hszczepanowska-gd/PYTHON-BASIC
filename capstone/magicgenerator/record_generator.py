import ast
import logging
import random
import re
import time
import uuid
from typing import Optional

RAND_RANGE_RE = re.compile(r'^\s*rand\(\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*$')
ALLOWED_TYPES = ["str", "int", "timestamp"]

class SchemaError(Exception):
    pass

class RecordGenerator:
    def __init__(self, schema: dict, log: logging.Logger) -> None:
        self.schema = schema
        self.log = log

    def generate_row_from_schema(self) -> dict:
        out = {}

        for key, value in self.schema.items():
            if not isinstance(value, str):
                raise SchemaError(f"Value for '{key}' must be string; got {type(value).__name__}")
            
            value = value.strip()
            if ":" in value and value.split(":", 1)[0].strip() in ALLOWED_TYPES:
                dtype, data = value.split(":", 1)
                dtype, data = dtype.strip(), data.strip()

                if dtype == "timestamp":
                    if data:
                        self.log.warning("Field '%s': timestamp ignores value after ':'.", key)
                    out[key] = time.time()
                    continue

                if dtype == "str":
                    out[key] = self._gen_str_value(key, data)
                    continue

                if dtype == "int":
                    out[key] = self._gen_int_value(key, data)
                    continue

                raise SchemaError(f"Field '{key}': unknown type '{dtype}'")

            raise SchemaError(
                f"Field '{key}': value must be 'type:...' or list literal '[...]', got {value!r}"
            )

        return out

    @staticmethod
    def _gen_str_value(field: str, data: str) -> str:
        if data == "":
            return ""
        if data == "rand":
            return str(uuid.uuid4())
        if data.startswith("[") and data.endswith("]"):
            lst = ast.literal_eval(data)
            if not all(isinstance(x, str) for x in lst):
                raise SchemaError(f"Field '{field}': str:[...] expects a list of strings.")
            return random.choice(lst)
        return data

    @staticmethod
    def _gen_int_value(field: str, data: str) -> Optional[int]:
        if data == "":
            return None
        if data == "rand":
            return random.randint(0, 10000)
        m = RAND_RANGE_RE.match(data)
        if m:
            lo, hi = int(m.group(1)), int(m.group(2))
            if lo > hi:
                raise SchemaError(f"Field '{field}': rand(from,to) requires from <= to.")
            return random.randint(lo, hi)
        if data.startswith("[") and data.endswith("]"):
            lst = ast.literal_eval(data)
            try:
                ints = [int(x) for x in lst]
            except Exception:
                raise SchemaError(f"Field '{field}': int:[...] must contain only integers.")
            return random.choice(ints)
        try:
            return int(data)
        except ValueError:
            raise SchemaError(f"Field '{field}': {data!r} cannot be converted to int.")
