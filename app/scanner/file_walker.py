"""
File walker.

Yields every file under a repository, relative to the repo root, skipping
the .git directory and anything matched by the repo's own .gitignore.
Policies that need to inspect file contents (no_secrets, large_files,
etc.) use this instead of walking the filesystem themselves, so .gitignore
handling lives in exactly one place.
"""

from pathlib import Path
from typing import Iterator

import pathspec


def walk_files(repo_path: str) -> Iterator[Path]:
    """
    Yield every file under repo_path as a Path relative to repo_path.
    """
    root = Path(repo_path)
    spec = _load_gitignore(root)

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue

        relative = path.relative_to(root)

        if relative.parts[0] == ".git":
            continue
        if spec.match_file(str(relative)):
            continue

        yield relative


def _load_gitignore(root: Path) -> pathspec.PathSpec:
    gitignore_path = root / ".gitignore"
    if not gitignore_path.is_file():
        return pathspec.PathSpec.from_lines("gitignore", [])
    return pathspec.PathSpec.from_lines(
        "gitignore", gitignore_path.read_text().splitlines()
    )
