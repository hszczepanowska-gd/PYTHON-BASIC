from __future__ import annotations
import argparse
from dataclasses import dataclass


@dataclass
class ParsedConfig:
    path_to_save_files: str
    file_name: str
    data_schema: str
    data_lines: int
    log_level: str


class ConfigManager:
    def __init__(self, prog: str = "magicgenerator") -> None:
        self.prog = prog

    def _build_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description="Generate JSON test data from a simple schema.",
        )
        parser.add_argument(
            "--path_to_save_files",
            default=".",
            help="Path to the directory where output files will be saved. Default: %(default)s",
        )
        parser.add_argument(
            "--file_name",
            default="data",
            help="Base name for the output file (without extension). Default: %(default)s",
        )
        parser.add_argument(
            "--data_schema",
            required=True,
            help=("JSON schema as a string or path to a .json file."),
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
        return parser

    def parse(self) -> ParsedConfig:
        parser = self._build_parser()
        args = parser.parse_args()
        return ParsedConfig(
            path_to_save_files=args.path_to_save_files,
            file_name=args.file_name,
            data_schema=args.data_schema,
            data_lines=args.data_lines,
            log_level=args.log_level,
        )
