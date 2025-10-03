from __future__ import annotations
import logging
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
                row = generator.generate_one()
                writer.write_record(row)
        except SchemaError:
            raise
        except Exception as e:
            raise
        finally:
            writer.close()

        self.log.info("Finished generation: %s", out_path)
