import argparse
import configparser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParsedConfig:
    path_to_save_files: str
    file_name: str
    data_schema: str
    data_lines: int
    log_level: str
    files_count: int    
    file_prefix: str
    clear_path: bool
    multiprocessing: int


class ConfigManager:
    def __init__(self, prog: str = "magicgenerator", defaults_path: str = "default.ini") -> None:
        self.prog = prog
        self.defaults_path = Path(defaults_path)

    def _build_parser(self, default_values: dict) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description="Generate JSON test data from a simple schema.",
        )
        parser.add_argument(
            "--path_to_save_files",
            default=default_values.get("path_to_save_files", "."),
            help="Path to the directory where output files will be saved. Default: %(default)s",
        )
        parser.add_argument(
            "--file_name",
            default=default_values.get("file_name", "data"),
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
            default=default_values.get("data_lines", 1000),
            help="Number of records to generate. Default: %(default)s",
        )
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR"],
            default=default_values.get("log_level", "INFO"),
            help="Logging level. Default: %(default)s",
        )
        parser.add_argument(
            "--files_count",
            type=int,
            default=default_values.get("files_count", 1),
            help="How many files to generate. 0 = print to stdout instead of files. Default: %(default)s",
        )
        parser.add_argument(
            "--file_prefix",
            choices=["count", "random", "uuid"],
            default=default_values.get("file_prefix", "count"),
            help="Prefix strategy when generating more than 1 file: count | random | uuid. Default: %(default)s",
        )
        parser.add_argument(
            "--clear_path", 
            action="store_true",
            default=default_values.get("clear_path", False),
            help="If set, delete existing files matching file_name before generation."
        )
        parser.add_argument(
            "--multiprocessing",
            type=int,
            default=default_values.get("multiprocessing", 1),
            help="Number of processes to use when creating files in parallel. Default: %(default)s",
        )
        return parser

    def parse(self) -> ParsedConfig:
        cfg = configparser.ConfigParser()

        if self.defaults_path.exists():
            cfg.read(self.defaults_path, encoding="utf-8")
            d = cfg["DEFAULT"]
        else:
            raise FileNotFoundError(f"Default config file not found: {self.defaults_path}")

        parser = self._build_parser(default_values=d)
        args = parser.parse_args()
        return ParsedConfig(
            path_to_save_files=args.path_to_save_files,
            file_name=args.file_name,
            data_schema=args.data_schema,
            data_lines=args.data_lines,
            log_level=args.log_level,
            files_count=args.files_count,
            file_prefix=args.file_prefix,
            clear_path=args.clear_path,
            multiprocessing=args.multiprocessing,
        )
