"""
Write tests for 2_python_part_2/task_read_write.py task.
To write files during tests use temporary files:
https://docs.python.org/3/library/tempfile.html
https://docs.pytest.org/en/6.2.x/tmpdir.html
"""

from pathlib import Path
import pytest

module = __import__('2_python_part_2.task_read_write', fromlist=['process_all_files_into_one'])
process_all_files_into_one = module.process_all_files_into_one

def test_process_all_files_into_one(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    files_dir = tmp_path / "test-files"
    files_dir.mkdir()

    (files_dir / "file_1.txt").write_text("23", encoding="utf-8")
    (files_dir / "file_2.txt").write_text("78", encoding="utf-8")
    (files_dir / "file_3.txt").write_text("3", encoding="utf-8")

    process_all_files_into_one(files_dir)

    result_file = tmp_path / "result.txt"
    assert result_file.exists()
    assert result_file.read_text(encoding="utf-8") == "23, 78, 3"