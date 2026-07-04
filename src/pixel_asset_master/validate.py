"""Asset validation command."""

import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    HAS_PIL = False

from pixel_asset_master.common import load_palette, parse_base_size, parse_max_colors


def cmd_validate_assets(project_path_str: str, strict: bool = True) -> bool:
    """Run full asset validation against project specifications.

    Args:
        project_path_str: Path to the project directory.
        strict: If True, semi-transparent pixels and anti-aliasing are treated as errors.
    """
    project_path = Path(project_path_str)
    spec_lock = project_path / "spec_lock.md"
    assets_dir = project_path / "assets"

    if not spec_lock.exists():
        print("[ERROR] spec_lock.md not found")
        return False

    if not assets_dir.exists():
        print("[WARN] No assets directory yet")
        return True

    palette_colors = set(load_palette(project_path))
    base_size = parse_base_size(project_path)
    max_colors = parse_max_colors(project_path)

    print(f"Spec: base_size={base_size}, max_colors={max_colors}, palette={len(palette_colors)} colors")

    if not HAS_PIL:
        print("[WARN] Pillow not installed, limited validation")
        return _validate_structure_only(project_path)

    errors = []
    warnings = []
    total_assets = 0

    # Group animation frames by asset name for consistency checks.
    animation_groups: dict[str, list[Path]] = defaultdict(list)

    for png in sorted(assets_dir.rglob("*.png")):
        total_assets += 1
        result = _validate_single_asset(png, palette_colors, base_size, max_colors, strict=strict)
        errors.extend(result["errors"])
        warnings.extend(result["warnings"])

        # Collect animation frames: e.g. player_idle_01.png -> player_idle
        m = re.match(r"(.+)_(\d{2,})\.png$", png.name)
        if m:
            animation_groups[m.group(1)].append(png)

    # Animation frame consistency checks.
    for anim_name, frames in sorted(animation_groups.items()):
        if len(frames) < 2:
            continue
        first = Image.open(frames[0]).size
        for f in frames[1:]:
            size = Image.open(f).size
            if size != first:
                errors.append(
                    f"animation '{anim_name}': frame size mismatch {first} vs {size} ({f.name})"
                )

    struct_ok = _validate_structure_only(project_path, quiet=True)

    print(f"\n{'=' * 60}")
    print(f"[SCAN] Checked {total_assets} asset(s)")
    if errors:
        print(f"  [ERROR] {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
    if warnings:
        print(f"  [WARN] {len(warnings)} warning(s):")
        for w in warnings:
            print(f"    - {w}")
    if not errors and not warnings:
        print("  [OK] All assets passed validation")
    elif not errors:
        print("  [OK] Passed with warnings")

    return len(errors) == 0 and struct_ok


def _validate_single_asset(
    png: Path,
    palette_colors: set[str],
    base_size: tuple[int, int] | None,
    max_colors: int,
    strict: bool,
) -> dict[str, list[str]]:
    """Validate a single PNG asset. Returns {'errors': [...], 'warnings': [...]}."""
    errors: list[str] = []
    warnings: list[str] = []

    img = Image.open(png)
    w, h = img.size

    if base_size:
        bw, bh = base_size
        if w % bw != 0 or h % bh != 0:
            if w != bw or h != bh:
                warnings.append(f"{png.name}: size {w}x{h} not a multiple of base {bw}x{bh}")

    img_rgba = img.convert("RGBA")
    pixels = list(img_rgba.getdata())
    unique_colors = set()
    out_of_palette = set()
    semi_transparent = 0

    for r, g, b, a in pixels:
        if a == 0:
            continue
        if 0 < a < 255:
            semi_transparent += 1
            continue
        hex_c = f"#{r:02X}{g:02X}{b:02X}"
        unique_colors.add(hex_c)
        if palette_colors and hex_c.upper() not in palette_colors:
            out_of_palette.add(hex_c)

    if len(unique_colors) > max_colors:
        errors.append(f"{png.name}: {len(unique_colors)} colors exceeds budget of {max_colors}")

    if out_of_palette:
        errors.append(f"{png.name}: {len(out_of_palette)} color(s) outside declared palette")

    if semi_transparent > 0:
        msg = f"{png.name}: {semi_transparent} semi-transparent pixels (possible anti-aliasing)"
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    # Simple anti-aliasing / feathering detector: count edge pixels whose neighbours
    # contain many distinct intermediate colours.
    aa_score = _detect_anti_aliasing(img_rgba, palette_colors)
    if aa_score > 0:
        msg = f"{png.name}: {aa_score} suspicious anti-aliased edge pixel(s)"
        if strict:
            errors.append(msg)
        else:
            warnings.append(msg)

    return {"errors": errors, "warnings": warnings}


def _detect_anti_aliasing(img: Image.Image, palette_colors: set[str]) -> int:
    """Return the number of edge pixels that look like anti-aliasing intermediates.

    Heuristic: an opaque edge pixel is suspicious if most of its 8 neighbours are
    transparent and its colour is not in the declared palette.
    """
    if not palette_colors:
        return 0

    w, h = img.size
    pixels = list(img.getdata())
    suspicious = 0

    def hex_at(idx: int) -> str | None:
        r, g, b, a = pixels[idx]
        if a < 128:
            return None
        return f"#{r:02X}{g:02X}{b:02X}".upper()

    for y in range(h):
        for x in range(w):
            idx = y * w + x
            c = hex_at(idx)
            if c is None or c in palette_colors:
                continue
            # Count transparent neighbours.
            transparent_neighbours = 0
            total_neighbours = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        total_neighbours += 1
                        if pixels[ny * w + nx][3] < 128:
                            transparent_neighbours += 1
            if total_neighbours and transparent_neighbours / total_neighbours >= 0.5:
                suspicious += 1

    return suspicious


def _validate_structure_only(project_path: Path, quiet: bool = False) -> bool:
    """Validate only directory and required-file structure."""
    required_dirs = ["assets", "images", "animations", "sheets", "notes", "exports"]
    required_files = ["design_spec.md", "spec_lock.md"]
    issues = []

    for d in required_dirs:
        if not (project_path / d).exists():
            issues.append(f"Missing directory: {d}")

    for f in required_files:
        if not (project_path / f).exists():
            issues.append(f"Missing file: {f}")

    if issues:
        if not quiet:
            for i in issues:
                print(f"  [WARN] {i}")
        return False
    return True


def main_entry(project_path_str: str) -> None:
    ok = cmd_validate_assets(project_path_str)
    sys.exit(0 if ok else 1)
