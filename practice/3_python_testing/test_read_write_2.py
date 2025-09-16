"""
Write tests for 2_python_part_2/task_read_write_2.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""
from pathlib import Path
import pytest
from unittest.mock import patch

module = __import__("2_python_part_2.task_read_write_2",  fromlist=["generate_words", "write_words_to_files"])
write_words_to_files = module.write_words_to_files

def test_write_words_to_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    with patch.object(module, "generate_words", return_value=["abc", "def", "xyz"]):
        write_words_to_files()

    f1 = tmp_path / "file1.txt"
    assert f1.exists()
    assert f1.read_text(encoding="utf-8") == "abc\ndef\nxyz"

    f2 = tmp_path / "file2.txt"
    assert f2.exists()
    assert f2.read_text(encoding="cp1252") == "xyz,def,abc"
