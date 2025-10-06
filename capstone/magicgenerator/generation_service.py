from __future__ import annotations
import json
import logging
import random
import uuid
from pathlib import Path

from record_generator import RecordGenerator, SchemaError
from jsonlines_writer import JsonLinesWriter


class GenerationService:
    def __init__(self, logger: logging.Logger) -> None:
        self.log = logger

    def generate_to_file(self, schema: dict, out_path: Path, lines: int) -> None:
        self.log.info("Starting generation: %d lines -> %s", lines, out_path)
        generator = RecordGenerator(schema, self.log)
        writer = JsonLinesWriter(out_path, self.log)

        try:
            writer.open()
            for _ in range(lines):
                row = generator.generate_row_from_schema()
                writer.write_record(row)
        finally:
            writer.close()

        self.log.info("Finished generation: %s", out_path)

    def generate_many_files(
        self,
        schema: dict,
        out_dir: Path,
        base_name: str,
        lines_per_file: int,
        files_count: int,
        prefix_mode: str,
    ) -> None:
        self.log.info(
            "Starting multi-file generation: %d files × %d lines -> %s",
            files_count, lines_per_file, out_dir
        )

        for i in range(files_count):
            suffix = self._build_suffix(prefix_mode, i)
            filename = f"{base_name}_{suffix}.jsonl"
            self.generate_to_file(schema, out_dir / filename, lines_per_file)

        self.log.info("Finished multi-file generation")

    def _build_suffix(self, mode: str, idx: int) -> str:
        if mode == "count":
            return f"{idx + 1:03d}"
        if mode == "random":
            return f"{random.randint(0, 999999):06d}"
        if mode == "uuid":
            return str(uuid.uuid4())
        return f"{idx + 1:03d}"
