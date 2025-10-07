import json
import logging
import os
import sys
from pathlib import Path
import time
from generation_service import GenerationService
from record_generator import SchemaError
from config_manager import ConfigManager

class AppCLI:
    def __init__(self) -> None:
        self.logger = logging.getLogger("magicgenerator")
        self.config_manager = ConfigManager()

    def configure_logging(self, level: str) -> None:
        logging.basicConfig(
            level=getattr(logging, level),
            format="%(asctime)s | %(levelname)s | %(message)s",
        )
        self.logger.setLevel(getattr(logging, level))

    def _resolve_output_dir(self, path_arg: str) -> Path:
        p = Path(path_arg).expanduser().resolve()
        if p.exists() and not p.is_dir():
            self.logger.error("Given path exists, but is not a directory: %s", p)
            sys.exit(1)
        if not p.exists():
            try:
                p.mkdir(parents=True, exist_ok=True)
            except OSError as e:
                self.logger.error("Failed to create directory '%s': %s", p, e)
                sys.exit(1)
        return p

    def _load_schema(self, schema_arg: str) -> dict:
        file_path = Path(schema_arg).expanduser()
        if file_path.exists() and file_path.is_file():
            try:
                text = file_path.read_text(encoding="utf-8")
                return json.loads(text)
            except (OSError, json.JSONDecodeError) as e:
                self.logger.error("Error loading/parsing schema from file '%s': %s", file_path, e)
                sys.exit(1)

        try:
            return json.loads(schema_arg)
        except json.JSONDecodeError as e:
            self.logger.error(
                "Invalid JSON in --data-schema. Provide a path to a .json file or a valid JSON string. Details: %s",
                e,
            )
            sys.exit(1)

    def run(self) -> None:
        cfg = self.config_manager.parse()
        self.configure_logging(cfg.log_level)
        start_time = time.time()
        self.logger.info("Start magicgenerator")
        self.logger.debug("Arguments: %s", vars(cfg))

        out_dir = self._resolve_output_dir(cfg.path_to_save_files)

        raw_schema = self._load_schema(cfg.data_schema)
        self.logger.info("Loaded schema (keys: %s)", ", ".join(raw_schema.keys()))


        out_path = out_dir / f"{cfg.file_name}.jsonl"
        self.logger.info("Output file: %s", out_path)
        service = GenerationService(self.logger)
        try:

            out_dir = self._resolve_output_dir(cfg.path_to_save_files)
            if cfg.clear_path:
                deleted_count = service.clear_path(out_dir, cfg.file_name)
                self.logger.info("Cleared %d existing file(s) matching base name '%s'", deleted_count, cfg.file_name)

            if cfg.files_count == 1 or cfg.multiprocessing == 1:

                if cfg.files_count == 1:
                    out_path = out_dir / f"{cfg.file_name}.jsonl"
                    self.logger.info("Output file: %s", out_path)
                    service.generate_to_file(raw_schema, out_path, cfg.data_lines)
                else:
                    self.logger.info("Output dir (multi): %s", out_dir)
                    service.generate_many_files(
                        schema=raw_schema,
                        out_dir=out_dir,
                        base_name=cfg.file_name,
                        lines_per_file=cfg.data_lines,
                        files_count=cfg.files_count,
                        prefix_mode=cfg.file_prefix,
                    )
            else:
                cpu = os.cpu_count() or 1
                proc = cfg.multiprocessing
                if proc < 0:
                    self.logger.error("--multiprocessing must be >= 0")
                    sys.exit(1)
                if proc == 0:
                    self.logger.warning("--multiprocessing=0 is not useful. Using 1.")
                    proc = 1
                if proc > cpu:
                    self.logger.warning("--multiprocessing=%d > os.cpu_count()=%d. Using %d.", proc, cpu, cpu)
                    proc = cpu

                service.generate_many_files_parallel(
                    schema=raw_schema,
                    out_dir=out_dir,
                    base_name=cfg.file_name,
                    lines_per_file=cfg.data_lines,
                    files_count=cfg.files_count,
                    prefix_mode=cfg.file_prefix,
                    process_count=proc,
                )
                    
        except SchemaError as e:
            self.logger.error("Schema error: %s", e)
            sys.exit(1)
        except Exception as e:
            self.logger.error("Unexpected error during generation: %s", e)
            sys.exit(1)

        end_time = time.time()
        elapsed = end_time - start_time
        self.logger.info("Elapsed time: %.2f seconds", elapsed)


def main() -> None:
    AppCLI().run()

if __name__ == "__main__":
    main()