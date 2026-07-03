"""Project management commands: init, import-sources, validate-project."""

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from pixel_asset_master.common import ASSET_CATEGORIES, projects_dir, resolve_root

# Minimal fallback palette used when no palette source is available.
FALLBACK_PALETTE: list[str] = ["#000000", "#FFFFFF"]


def _load_workspace_palettes(root_override: str | None = None) -> list[dict]:
    """Load palette library from the workspace skill template if it exists.

    Path: ``<root>/skills/pixel-asset-master/templates/palettes/palettes_index.json``
    """
    workspace_json = (
        resolve_root(root_override)
        / "skills"
        / "pixel-asset-master"
        / "templates"
        / "palettes"
        / "palettes_index.json"
    )
    if workspace_json.exists():
        try:
            return json.loads(workspace_json.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _load_palette_file(path: str, palette_name: str | None = None) -> list[str]:
    """Load a palette from a JSON file.

    Supported formats:
      - A list of hex strings: ``["#FF0000", "#00FF00"]``
      - A single palette object: ``{"name": "...", "hex": ["#FF0000", ...]}``
      - A palette index (list of palette objects): matches ``palette_name`` if given,
        otherwise uses the first palette's ``hex`` list.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list) and data and isinstance(data[0], dict):
        # Palette index format
        for palette in data:
            if palette_name and palette.get("name", "").lower() == palette_name.lower():
                return [str(c) for c in palette.get("hex", [])]
        return [str(c) for c in data[0].get("hex", [])]
    if isinstance(data, dict):
        return [str(c) for c in data.get("hex", [])]
    if isinstance(data, list):
        return [str(c) for c in data]
    return []


def resolve_palette(
    palette_name: str,
    palette_file: str | None,
    palette_colors: list[str] | None,
    root: str | None = None,
) -> tuple[list[str], str]:
    """Resolve the final palette hex list and canonical name.

    Priority:
      1. ``--palette-colors`` comma-separated hex values
      2. ``--palette-file`` JSON file
      3. Named palette from workspace ``palettes_index.json``
      4. Fallback black/white
    """
    if palette_colors:
        return palette_colors, palette_name or "custom"

    if palette_file:
        try:
            return _load_palette_file(palette_file, palette_name=palette_name), palette_name or "custom"
        except (json.JSONDecodeError, OSError) as exc:
            print(f"[ERROR] Failed to load palette file: {exc}")
            sys.exit(1)

    if palette_name:
        for palette in _load_workspace_palettes(root):
            if palette["name"].lower() == palette_name.lower():
                return palette["hex"], palette["name"]
        # Named palette not found in workspace index: keep the name but use fallback colors.
        return list(FALLBACK_PALETTE), palette_name

    return list(FALLBACK_PALETTE), "custom"


def cmd_init(
    project_name: str,
    size: str,
    palette_name: str,
    palette_file: str | None = None,
    palette_colors: list[str] | None = None,
    root: str | None = None,
) -> None:
    """Initialize a new pixel art asset project."""
    projects_root = projects_dir(root)

    try:
        w_str, h_str = size.lower().split("x")
        w_int, h_int = int(w_str), int(h_str)
    except ValueError:
        print(f"[ERROR] Invalid size format: {size}. Expected WxH (e.g. 32x32)")
        sys.exit(1)

    max_size = 2048
    if w_int > max_size or h_int > max_size:
        print(f"[ERROR] Size {size} exceeds maximum {max_size}x{max_size}")
        sys.exit(1)
    if w_int < 1 or h_int < 1:
        print("[ERROR] Size is too small. Minimum 1x1.")
        sys.exit(1)

    date_str = datetime.now().strftime("%Y%m%d")
    full_name = f"{project_name}_{size}_{date_str}"
    project_path = projects_root / full_name

    if project_path.exists():
        print(f"[ERROR] Project already exists: {project_path}")
        sys.exit(1)

    project_path.mkdir(parents=True, exist_ok=True)
    for cat in ASSET_CATEGORIES:
        (project_path / "assets" / cat).mkdir(parents=True, exist_ok=True)
    for subdir in ["images", "animations", "sheets", "notes", "exports"]:
        (project_path / subdir).mkdir(parents=True, exist_ok=True)

    palette_hex, canonical_name = resolve_palette(
        palette_name, palette_file, palette_colors, root=root
    )
    _generate_initial_spec_lock(project_path, project_name, size, canonical_name, palette_hex)
    _generate_initial_design_spec(project_path, project_name, size, canonical_name)

    print(f"[OK] Project initialized: {project_path}")
    print(f"     Size: {size}")
    print(f"     Palette: {canonical_name}")
    print(f"     Categories: {', '.join(ASSET_CATEGORIES)}")


def cmd_import_sources(project_path_str: str, files: list[str], move: bool = False) -> None:
    """Import reference images into a project."""
    project_path = Path(project_path_str)
    if not project_path.exists():
        print(f"[ERROR] Project not found: {project_path}")
        sys.exit(1)

    images_dir = project_path / "images"
    imported = []

    for src in files:
        src_path = Path(src)
        if not src_path.exists():
            print(f"[WARN] File not found, skipping: {src}")
            continue

        dst = images_dir / src_path.name
        if move:
            shutil.move(str(src_path), str(dst))
        else:
            shutil.copy2(str(src_path), str(dst))
        imported.append(dst.name)
        print(f"  Imported: {dst.name}")

    print(f"[OK] Imported {len(imported)} file(s) to {images_dir}")


def cmd_validate_project(project_path_str: str) -> bool:
    """Validate the structure of a pixel art asset project."""
    project_path = Path(project_path_str)
    if not project_path.exists():
        print(f"[ERROR] Project not found: {project_path}")
        return False

    issues = []

    for required in ["design_spec.md", "spec_lock.md"]:
        if not (project_path / required).exists():
            issues.append(f"Missing: {required}")

    for cat in ASSET_CATEGORIES:
        d = project_path / "assets" / cat
        if not d.exists():
            issues.append(f"Missing directory: assets/{cat}")

    for required_dir in ["images", "animations", "sheets", "notes", "exports"]:
        if not (project_path / required_dir).exists():
            issues.append(f"Missing directory: {required_dir}")

    spec_lock = project_path / "spec_lock.md"
    if spec_lock.exists():
        content = spec_lock.read_text(encoding="utf-8")
        if "palette" not in content:
            issues.append("spec_lock.md missing palette section")
        if "canvas" not in content:
            issues.append("spec_lock.md missing canvas section")

    if issues:
        print(f"[WARN] Validation found {len(issues)} issue(s):")
        for issue in issues:
            print(f"  - {issue}")
        return False

    print("[OK] Project validation passed")
    return True


def _generate_initial_spec_lock(
    project_path: Path, name: str, size: str, palette_name: str, palette_hex: list[str]
) -> None:
    colors_yaml = "\n".join(f"  - {c}" for c in palette_hex)
    content = f"""# Execution Lock

## canvas
- base_size: {size}
- tile_size: {size}
- format: RGBA PNG

## palette
- name: {palette_name}
- colors:
{colors_yaml}

## style
- sub_style: outlined
- outline_color: #000000
- shading: 3-tone
- dithering: none
- light_direction: top-left

## per_sprite_budget
- max_colors: 16

## assets
- characters: []
- tiles: []
- items: []
- ui: []
- effects: []
- backgrounds: []

## forbidden
- Anti-aliasing
- Gradient fills
- Partial opacity (1-254 alpha)
- Colors outside declared palette
- Sub-pixel rendering
"""
    (project_path / "spec_lock.md").write_text(content, encoding="utf-8")


def _generate_initial_design_spec(
    project_path: Path, name: str, size: str, palette_name: str
) -> None:
    content = f"""# {name} - Design Spec

> Human-readable design narrative. Machine-readable contract: spec_lock.md.

## I. Project Information

| Item | Value |
| ---- | ----- |
| **Project Name** | {name} |
| **Canvas Size** | {size} |
| **Asset Count** | TBD |
| **Art Style** | TBD |
| **Target Platform** | TBD |
| **Color Palette** | {palette_name} |
| **Created Date** | {datetime.now().strftime("%Y-%m-%d")} |

---

## II-VIII. Sections to be filled by Strategist

(See templates/design_spec_reference.md for full structure)
"""
    (project_path / "design_spec.md").write_text(content, encoding="utf-8")
