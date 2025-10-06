from __future__ import annotations
import json
import logging
from pathlib import Path

class JsonLinesWriter:
    def __init__(self, path: Path, logger: logging.Logger) -> None:
        self.path = Path(path)
        self.log = logger
        self._fh = None

    def open(self) -> None:
        try:
            self._fh = self.path.open("w", encoding="utf-8")
        except OSError as e:
            self.log.error("Failed to open '%s' for writing: %s", self.path, e)
            raise

    def write_record(self, record: dict) -> None:
        if self._fh is None:
            raise RuntimeError("Writer not opened. Call open() first.")
        try:
            line = json.dumps(record, ensure_ascii=False)
            self._fh.write(line + "\n")
        except OSError as e:
            self.log.error("Failed to write to '%s': %s", self.path, e)
            raise

    def close(self) -> None:
        if self._fh is not None:
            self._fh.close()
            self._fh = None
