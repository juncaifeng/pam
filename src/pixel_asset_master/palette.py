"""Palette extraction and validation commands."""

import sys
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    HAS_PIL = False

from pixel_asset_master.common import load_palette


def cmd_extract(image_path: str, count: int = 16) -> None:
    """Extract a palette from a reference image."""
    if not HAS_PIL:
        print("[ERROR] Pillow required: pip install Pillow")
        sys.exit(1)

    img = Image.open(image_path).convert("RGBA")
    pixels = list(img.getdata())
    opaque = [(r, g, b) for r, g, b, a in pixels if a > 128]

    if not opaque:
        print("[ERROR] No opaque pixels found in image")
        return

    color_counts: dict[tuple[int, int, int], int] = {}
    for r, g, b in opaque:
        qr = (r >> 4) << 4
        qg = (g >> 4) << 4
        qb = (b >> 4) << 4
        key = (qr, qg, qb)
        color_counts[key] = color_counts.get(key, 0) + 1

    sorted_colors = sorted(color_counts.items(), key=lambda x: -x[1])

    palette = []
    for (r, g, b), _ in sorted_colors:
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        too_close = False
        for existing in palette:
            er = int(existing[1:3], 16)
            eg = int(existing[3:5], 16)
            eb = int(existing[5:7], 16)
            dist = ((r - er) ** 2 + (g - eg) ** 2 + (b - eb) ** 2) ** 0.5
            if dist < 30:
                too_close = True
                break
        if not too_close:
            palette.append(hex_color)
        if len(palette) >= count:
            break

    print(f"Extracted {len(palette)} colors:")
    for c in palette:
        print(f"  {c}")


def cmd_validate(project_path_str: str) -> None:
    """Validate that project assets only use declared palette colors."""
    if not HAS_PIL:
        print("[ERROR] Pillow required: pip install Pillow")
        sys.exit(1)

    project_path = Path(project_path_str)
    palette_colors = set(load_palette(project_path))

    if not palette_colors:
        print("[WARN] No palette colors found in spec_lock.md")
        return

    print(f"Declared palette: {len(palette_colors)} colors")

    assets_dir = project_path / "assets"
    if not assets_dir.exists():
        print("[WARN] No assets directory yet")
        return

    issues = []
    for png in assets_dir.rglob("*.png"):
        img = Image.open(png).convert("RGBA")
        pixels = list(img.getdata())
        for r, g, b, a in pixels:
            if a < 128:
                continue
            hex_c = f"#{r:02X}{g:02X}{b:02X}"
            if hex_c.upper() not in palette_colors:
                issues.append(f"{png.name}: color {hex_c} not in palette")
                break

    if issues:
        print(f"[WARN] {len(issues)} asset(s) with out-of-palette colors:")
        for issue in issues[:20]:
            print(f"  - {issue}")
    else:
        print("[OK] All assets use declared palette colors")


def cmd_distance(color1: str, color2: str) -> None:
    """Calculate Euclidean distance between two hex colors."""
    r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
    r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
    dist = ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5
    print(f"Distance: {dist:.1f} (max=441.7)")
