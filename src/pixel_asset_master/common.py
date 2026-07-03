"""Shared helpers for Pixel Asset Master CLI."""

import os
from pathlib import Path

ASSET_CATEGORIES = ["characters", "tiles", "items", "ui", "effects", "backgrounds"]


def resolve_root(root_override: str | None = None) -> Path:
    """Resolve the workspace root directory.

    Priority:
      1. Explicit ``root_override`` (usually from --root).
      2. ``PAM_PROJECTS_ROOT`` environment variable.
      3. Current working directory.

    The generated projects live under ``<root>/projects``.
    """
    if root_override:
        return Path(root_override).resolve()

    env_root = os.environ.get("PAM_PROJECTS_ROOT")
    if env_root:
        return Path(env_root).resolve()

    return Path.cwd().resolve()


def projects_dir(root_override: str | None = None) -> Path:
    """Return the ``projects`` directory for the resolved workspace root."""
    return resolve_root(root_override) / "projects"


def load_palette(project_path: Path) -> list[str]:
    """Load declared palette hex colors from ``spec_lock.md``."""
    spec_lock = project_path / "spec_lock.md"
    if not spec_lock.exists():
        return []

    content = spec_lock.read_text(encoding="utf-8")
    palette = []
    in_palette = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## palette"):
            in_palette = True
            continue
        if line.startswith("## ") and in_palette:
            in_palette = False
            continue
        if in_palette and line.startswith("- #"):
            palette.append(line[2:].upper())
    return palette


def parse_base_size(project_path: Path) -> tuple[int, int] | None:
    """Parse ``base_size`` from ``spec_lock.md`` if present."""
    spec_lock = project_path / "spec_lock.md"
    if not spec_lock.exists():
        return None

    content = spec_lock.read_text(encoding="utf-8")
    in_canvas = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## canvas"):
            in_canvas = True
            continue
        if line.startswith("## ") and in_canvas:
            in_canvas = False
            continue
        if in_canvas and line.startswith("- base_size:"):
            size_str = line.split(":", 1)[1].strip()
            try:
                w, h = size_str.lower().split("x")
                return int(w), int(h)
            except ValueError:
                return None
    return None


def parse_max_colors(project_path: Path, default: int = 16) -> int:
    """Parse ``max_colors`` from ``spec_lock.md`` if present."""
    spec_lock = project_path / "spec_lock.md"
    if not spec_lock.exists():
        return default

    content = spec_lock.read_text(encoding="utf-8")
    in_budget = False
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("## per_sprite_budget"):
            in_budget = True
            continue
        if line.startswith("## ") and in_budget:
            in_budget = False
            continue
        if in_budget and line.startswith("- max_colors:"):
            try:
                return int(line.split(":", 1)[1].strip())
            except ValueError:
                return default
    return default
