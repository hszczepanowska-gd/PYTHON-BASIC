from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path

class AppCLI:
    def __init__(self) -> None:
        self.logger = logging.getLogger("magicgenerator")

    def parse_args(self) -> argparse.Namespace:
        parser = argparse.ArgumentParser(
            prog="magicgenerator",
            description="Generate JSON test data from a simple schema.",
        )

        parser.add_argument(
            "--path_to_save_files",
            help="Path to the directory where output files will be saved.",
        )

        parser.add_argument(
            "--file_name",
            default="data",
            help="Base name for the output file (without extension). Default: %(default)s",
        )

        parser.add_argument(
            "--data_schema",
            required=True,
            help=(
                "JSON schema as a string or path to a .json file defining the data structure."
                "Example string: "
                r"'{\"date\":\"timestamp:\",\"name\":\"str:rand\",\"age\":\"int:rand(1,90)\"}'"
            ),
        )

        parser.add_argument(
            "--data_lines",
            type=int,
            default=1000,
            help="Number of records to generate. Default: %(default)s",
        )

        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default="INFO",
            help="Logging level. Default: %(default)s",
        )


        return parser.parse_args()

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
        args = self.parse_args()
        self.configure_logging(args.log_level)

        self.logger.info("Start magicgenerator")
        self.logger.debug("Arguments: %s", vars(args))

        out_dir = self._resolve_output_dir(args.path_to_save_files)

        raw_schema = self._load_schema(args.data_schema)
        self.logger.info("Loaded schema (keys: %s)", ", ".join(raw_schema.keys()))


        out_path = out_dir / f"{args.file_name}.jsonl"
        self.logger.info("Output file: %s", out_path)

        try:
            self._generate_one_file_placeholder(
                schema=raw_schema,
                out_path=out_path,
                lines=args.data_lines,
            )
        except Exception as e:
            self.logger.error("Unexpected error during generation: %s", e)
            sys.exit(1)

        self.logger.info("Finished generation")

    def _generate_one_file_placeholder(self, schema: dict, out_path: Path, lines: int) -> None:
        self.logger.warning(
            "PLACEHOLDER GENERATION ACTIVATED: will write %d empty records to %s",
            lines, out_path
        )
        try:
            with out_path.open("w", encoding="utf-8") as f:
                for _ in range(lines):
                    f.write("{}\n")
        except OSError as e:
            self.logger.error("Failed to write file '%s': %s", out_path, e)
            sys.exit(1)


def main() -> None:
    AppCLI().run()


if __name__ == "__main__":
    main()