import json
import logging
import re
import sys
from pathlib import Path

import pytest

THIS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = THIS_DIR.parent
MG_DIR = PROJECT_ROOT / "magicgenerator"
if str(MG_DIR) not in sys.path:
    sys.path.insert(0, str(MG_DIR))

from cli import AppCLI
from generation_service import GenerationService
from record_generator import RecordGenerator, SchemaError


@pytest.fixture
def test_logger() -> logging.Logger:
    logger = logging.getLogger("magicgenerator.test")
    logger.setLevel(logging.DEBUG)
    return logger


@pytest.fixture
def sample_schema() -> dict:
    return {
        "date": "timestamp:",
        "name": "str:rand",
        "kind": "str:['client','partner','government']",
        "age": "int:rand(1, 3)",
        "maybe": "int:"
    }


class TestMagicGenerator:
    UUID_RE = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

    @pytest.mark.parametrize(
        "field_spec, validator",
        [
            ({"ts": "timestamp:"}, lambda v: isinstance(v, float)),
            ({"s": "str:"}, lambda v: v == ""),
            ({"s": "str:rand"}, lambda v: isinstance(v, str) and TestMagicGenerator.UUID_RE.match(v)),
            ({"s": "str:['a','b']"}, lambda v: v in {"a", "b"}),
            ({"s": "str:fixed"}, lambda v: v == "fixed"),
            ({"i": "int:"}, lambda v: v is None),
            ({"i": "int:rand"}, lambda v: isinstance(v, int) and 0 <= v <= 10000),
            ({"i": "int:rand(1, 3)"}, lambda v: v in {1, 2, 3}),
            ({"i": "int:[1,2,5]"}, lambda v: v in {1, 2, 5}),
            ({"i": "int:7"}, lambda v: v == 7),
        ],
    )
    def test_different_data_types(self, field_spec, validator, test_logger):
        gen = RecordGenerator(field_spec, test_logger)
        row = gen.generate_row_from_schema()
        assert len(row) == 1
        value = next(iter(row.values()))
        assert validator(value)

    @pytest.mark.parametrize(
        "schema",
        [
            {"date": "timestamp:", "name": "str:rand", "age": "int:rand(10, 20)"},
            {"date": "timestamp:", "type": "str:['client','partner']", "score": "int:[1,2,3]"},
            {"x": "str:hello", "y": "int:", "z": "int:42"},
        ],
    )
    def test_different_data_schemas(self, schema, test_logger):
        gen = RecordGenerator(schema, test_logger)
        row = gen.generate_row_from_schema()
        assert set(row.keys()) == set(schema.keys())
        for key, value in schema.items():
            v = row[key]
            if value.startswith("timestamp"):
                assert isinstance(v, float)
            elif value.startswith("str:"):
                assert isinstance(v, str)
            elif value.startswith("int:"):
                assert (v is None) or isinstance(v, int)

    def test_load_schema_from_json_file(self, tmp_path: Path):
        sample = {
            "date": "timestamp:",
            "name": "str:rand",
            "age": "int:rand(1, 3)"
        }
        p = tmp_path / "schema.json"
        p.write_text(json.dumps(sample), encoding="utf-8")

        cli = AppCLI()
        schema = cli._load_schema(str(p))
        assert isinstance(schema, dict)
        assert set(schema.keys()) == set(sample.keys())

    def test_clear_path_removes_files(self, tmp_path: Path, test_logger):

        base = "data"
        (tmp_path / f"{base}.jsonl").write_text("old\n", encoding="utf-8")
        (tmp_path / f"{base}_001.jsonl").write_text("old\n", encoding="utf-8")
        (tmp_path / f"{base}_abc.jsonl").write_text("old\n", encoding="utf-8")

        service = GenerationService(test_logger)
        deleted = service.clear_path(tmp_path, base)

        assert deleted == 3
        assert not (tmp_path / f"{base}.jsonl").exists()
        assert not (tmp_path / f"{base}_001.jsonl").exists()
        assert not (tmp_path / f"{base}_abc.jsonl").exists()

    def test_generate_to_file_saves_lines(self, tmp_path: Path, sample_schema: dict, test_logger):
        out_path = tmp_path / "out.jsonl"
        lines = 5

        service = GenerationService(test_logger)
        service.generate_to_file(sample_schema, out_path, lines)

        assert out_path.exists()
        content = out_path.read_text(encoding="utf-8").splitlines()
        assert len(content) == lines

        for line in content:
            obj = json.loads(line)
            assert set(obj.keys()) == set(sample_schema.keys())

    def test_generate_many_files_parallel_creates_expected_files(
        self, tmp_path: Path, sample_schema: dict, test_logger
    ):
        files_count = 4
        lines_per_file = 3
        base = "multi"
        prefix = "count"
        processes = 2

        service = GenerationService(test_logger)
        service.generate_many_files_parallel(
            schema=sample_schema,
            out_dir=tmp_path,
            base_name=base,
            lines_per_file=lines_per_file,
            files_count=files_count,
            prefix_mode=prefix,
            process_count=processes,
        )

        created = sorted(tmp_path.glob(f"{base}_*.jsonl"))
        assert len(created) == files_count
        for p in created:
            assert p.read_text(encoding="utf-8").splitlines().__len__() == lines_per_file

    def test_int_rand_range_inverted_raises(self, test_logger):
        schema = {"age": "int:rand(5, 1)"}
        gen = RecordGenerator(schema, test_logger)
        with pytest.raises(SchemaError):
            _ = gen.generate_row_from_schema()

    def test_cli_load_schema_invalid_json_exits(self, caplog):
        cli = AppCLI()
        bad_json = '{"date": "timestamp:", "x": }'
        with caplog.at_level(logging.ERROR), pytest.raises(SystemExit) as exc:
            _ = cli._load_schema(bad_json)

        assert exc.value.code == 1
        assert any("Invalid JSON in --data-schema" in rec.getMessage() for rec in caplog.records)
