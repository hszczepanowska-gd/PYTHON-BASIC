from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path
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
            format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
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

        self.logger.info("Start magicgenerator")
        self.logger.debug("Arguments: %s", vars(cfg))

        out_dir = self._resolve_output_dir(cfg.path_to_save_files)

        raw_schema = self._load_schema(cfg.data_schema)
        self.logger.info("Loaded schema (keys: %s)", ", ".join(raw_schema.keys()))


        out_path = out_dir / f"{cfg.file_name}.jsonl"
        self.logger.info("Output file: %s", out_path)
        service = GenerationService(self.logger)
        try:
            service.generate_to_file(
                schema=raw_schema,
                out_path=out_path,
                lines=cfg.data_lines,
            )
        except SchemaError as e:
            self.logger.error("Schema error: %s", e)
            sys.exit(1)
        except Exception as e:
            self.logger.error("Unexpected error during generation: %s", e)
            sys.exit(1)

        self.logger.info("Finished generation")


def main() -> None:
    AppCLI().run()

if __name__ == "__main__":
    main()