"""
Tests for the file walker, run against real temporary directories.
"""

from pathlib import Path

from app.scanner.file_walker import walk_files


def test_yields_file_at_root(tmp_path):
    (tmp_path / "a.txt").write_text("hello")

    paths = list(walk_files(str(tmp_path)))

    assert paths == [Path("a.txt")]


def test_yields_files_in_subdirectories(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("print('hi')")

    paths = list(walk_files(str(tmp_path)))

    assert Path("src/main.py") in paths


def test_skips_dot_git_directory(tmp_path):
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "HEAD").write_text("ref: refs/heads/main")
    (tmp_path / "real_file.txt").write_text("content")

    paths = list(walk_files(str(tmp_path)))

    assert paths == [Path("real_file.txt")]


def test_respects_gitignore_patterns(tmp_path):
    (tmp_path / ".gitignore").write_text("*.log\nbuild/\n")
    (tmp_path / "app.log").write_text("noisy")
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "output.txt").write_text("artifact")
    (tmp_path / "main.py").write_text("print('hi')")

    paths = list(walk_files(str(tmp_path)))

    assert paths == [Path(".gitignore"), Path("main.py")]


def test_returns_no_files_for_empty_repo(tmp_path):
    paths = list(walk_files(str(tmp_path)))

    assert paths == []


def test_missing_gitignore_does_not_raise(tmp_path):
    (tmp_path / "a.txt").write_text("hello")

    paths = list(walk_files(str(tmp_path)))

    assert paths == [Path("a.txt")]
