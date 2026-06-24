"""
File walker.

Yields every file under a repository, relative to the repo root, skipping
the .git directory and anything matched by the repo's own .gitignore.
Policies that need to inspect file contents (no_secrets, large_files,
etc.) use this instead of walking the filesystem themselves, so .gitignore
handling lives in exactly one place.

Walks with os.walk(..., followlinks=False) rather than Path.rglob, and
prunes ignored directories before descending into them. Both matter for
a tool that scans repos it doesn't control: a symlink pointing back up
the tree could otherwise turn the walk into an infinite loop, and
descending into an ignored directory (build/, node_modules/, etc.)
before filtering wastes work on potentially huge subtrees.
"""

import os
from pathlib import Path
from typing import Iterator

import pathspec


def walk_files(repo_path: str) -> Iterator[Path]:
    """
    Yield every file under repo_path as a Path relative to repo_path.
    """
    root = Path(repo_path)
    spec = _load_gitignore(root)
    relative_files: list[Path] = []

    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        relative_dir = Path(dirpath).relative_to(root)

        dirnames[:] = [
            name for name in dirnames if not _is_ignored_dir(relative_dir, name, spec)
        ]

        for filename in filenames:
            relative = relative_dir / filename
            if spec.match_file(str(relative)):
                continue
            relative_files.append(relative)

    return iter(sorted(relative_files))


def _is_ignored_dir(relative_dir: Path, name: str, spec: pathspec.PathSpec) -> bool:
    if name == ".git" and relative_dir == Path("."):
        return True
    return spec.match_file(f"{relative_dir / name}/")


def _load_gitignore(root: Path) -> pathspec.PathSpec:
    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file():
        return pathspec.PathSpec.from_lines("gitignore", [])
    return pathspec.PathSpec.from_lines(
        "gitignore", gitignore_path.read_text().splitlines()
    )
