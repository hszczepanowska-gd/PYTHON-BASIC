from __future__ import annotations
import json
import logging
from multiprocessing.pool import Pool
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
    
    def clear_path(self, out_dir: Path, base_name: str) -> int:
        patterns = [f"{base_name}.jsonl", f"{base_name}_*.jsonl"]
        to_delete = set()
        for pat in patterns:
            to_delete.update(out_dir.glob(pat))

        if not to_delete:
            return 0

        deleted = 0
        for p in to_delete:
            try:
                p.unlink()
                deleted += 1
                self.log.debug("clear_path: deleted %s", p)
            except OSError as e:
                raise OSError(f"Failed to delete '{p}': {e}") from e

        return deleted

    def _worker_generate_one_file(self, schema: dict, out_path: str, lines: int) -> None:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
        log = logging.getLogger("magicgenerator.worker")

        generator = RecordGenerator(schema, log)
        writer = JsonLinesWriter(Path(out_path), log)
        try:
            writer.open()
            for _ in range(lines):
                writer.write_record(generator.generate_row_from_schema())
        finally:
            writer.close()
            log.info("Finished generation: %s", out_path)

    def generate_many_files_parallel(self, schema: dict, out_dir: Path, base_name: str,
                                     lines_per_file: int, files_count: int,
                                     prefix_mode: str, process_count: int) -> None:
        self.log.info(
            "Starting multi-file multiprocessing generation with %d processes: %d files × %d lines -> %s",
            process_count, files_count, lines_per_file, out_dir
        )

        jobs = []
        for i in range(files_count):
            suffix = self._build_suffix(prefix_mode, i)
            out_path = str(Path(out_dir) / f"{base_name}_{suffix}.jsonl")
            jobs.append((schema, out_path, lines_per_file))

        with Pool(processes=process_count) as pool:
            pool.starmap(self._worker_generate_one_file, jobs)

        self.log.info("Parallel multi-file generation finished for %d files", files_count)

