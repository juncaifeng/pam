"""Asset validation command."""

import sys
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    HAS_PIL = False

from pixel_asset_master.common import load_palette, parse_base_size, parse_max_colors


def cmd_validate_assets(project_path_str: str) -> bool:
    """Run full asset validation against project specifications."""
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

    for png in sorted(assets_dir.rglob("*.png")):
        total_assets += 1
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

        for r, g, b, a in pixels:
            if a < 128:
                continue
            hex_c = f"#{r:02X}{g:02X}{b:02X}"
            unique_colors.add(hex_c)
            if palette_colors and hex_c.upper() not in palette_colors:
                out_of_palette.add(hex_c)

        if len(unique_colors) > max_colors:
            errors.append(f"{png.name}: {len(unique_colors)} colors exceeds budget of {max_colors}")

        if out_of_palette:
            errors.append(f"{png.name}: {len(out_of_palette)} color(s) outside declared palette")

        semi_transparent = sum(1 for _, _, _, a in pixels if 0 < a < 255)
        if semi_transparent > 0:
            warnings.append(
                f"{png.name}: {semi_transparent} semi-transparent pixels (possible anti-aliasing)"
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
