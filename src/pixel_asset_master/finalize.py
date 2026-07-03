"""Post-processing commands: quantize, clean, index."""

import sys
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    HAS_PIL = False

from pixel_asset_master.common import load_palette


def cmd_quantize(project_path_str: str) -> None:
    """Quantize all assets to the declared palette."""
    if not HAS_PIL:
        print("[ERROR] Pillow required: pip install Pillow")
        sys.exit(1)

    project_path = Path(project_path_str)
    palette = load_palette(project_path)
    if not palette:
        print("[ERROR] No palette found in spec_lock.md")
        sys.exit(1)

    print(f"Quantizing to {len(palette)} colors...")

    assets_dir = project_path / "assets"
    if not assets_dir.exists():
        print("[WARN] No assets directory")
        return

    count = 0
    for png in sorted(assets_dir.rglob("*.png")):
        img = Image.open(png).convert("RGBA")
        pixels = list(img.getdata())
        new_pixels = []
        for r, g, b, a in pixels:
            if a < 128:
                new_pixels.append((0, 0, 0, 0))
            else:
                nearest = _find_nearest(r, g, b, palette)
                new_pixels.append((*nearest, 255))

        img_quantized = Image.new("RGBA", img.size)
        img_quantized.putdata(new_pixels)
        img_quantized.save(png, "PNG")
        count += 1

    print(f"[OK] Quantized {count} asset(s)")


def cmd_clean(project_path_str: str) -> None:
    """Remove stray isolated pixels."""
    if not HAS_PIL:
        print("[ERROR] Pillow required")
        sys.exit(1)

    project_path = Path(project_path_str)
    assets_dir = project_path / "assets"
    if not assets_dir.exists():
        return

    count = 0
    for png in sorted(assets_dir.rglob("*.png")):
        img = Image.open(png).convert("RGBA")
        pixels = list(img.getdata())
        w, h = img.size

        changed = False
        new_pixels = list(pixels)

        for y in range(h):
            for x in range(w):
                idx = y * w + x
                r, g, b, a = pixels[idx]

                if a < 128:
                    continue

                neighbors = []
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < w and 0 <= ny < h:
                        nidx = ny * w + nx
                        nr, ng, nb, na = pixels[nidx]
                        if na >= 128:
                            neighbors.append((nr, ng, nb))

                if not neighbors:
                    new_pixels[idx] = (0, 0, 0, 0)
                    changed = True

        if changed:
            img_clean = Image.new("RGBA", img.size)
            img_clean.putdata(new_pixels)
            img_clean.save(png, "PNG")
            count += 1

    print(f"[OK] Cleaned stray pixels in {count} asset(s)")


def cmd_index(project_path_str: str) -> None:
    """Convert RGBA PNG assets to indexed PNG."""
    if not HAS_PIL:
        print("[ERROR] Pillow required")
        sys.exit(1)

    project_path = Path(project_path_str)
    palette = load_palette(project_path)

    assets_dir = project_path / "assets"
    if not assets_dir.exists():
        return

    pal_colors = []
    for hex_c in palette:
        r = int(hex_c[1:3], 16)
        g = int(hex_c[3:5], 16)
        b = int(hex_c[5:7], 16)
        pal_colors.append((r, g, b))

    count = 0
    for png in sorted(assets_dir.rglob("*.png")):
        img = Image.open(png).convert("RGBA")
        pixels = list(img.getdata())

        pal_img = Image.new("P", img.size)
        pal_data = []
        for r, g, b, a in pixels:
            if a < 128:
                pal_data.append(0)
            else:
                nearest_idx = _find_nearest_index(r, g, b, pal_colors)
                pal_data.append(nearest_idx)

        pal_img.putdata(pal_data)

        pal_rgb = [0, 0, 0]
        for r, g, b in pal_colors:
            pal_rgb.extend([r, g, b])
        while len(pal_rgb) < 768:
            pal_rgb.extend([0, 0, 0])

        pal_img.putpalette(pal_rgb)
        pal_img.info["transparency"] = 0
        pal_img.save(png, "PNG")
        count += 1

    print(f"[OK] Converted {count} asset(s) to indexed PNG")


def _find_nearest(r: int, g: int, b: int, palette_hex: list[str]) -> tuple[int, int, int]:
    best = (0, 0, 0)
    best_dist = float("inf")
    for hex_c in palette_hex:
        pr = int(hex_c[1:3], 16)
        pg = int(hex_c[3:5], 16)
        pb = int(hex_c[5:7], 16)
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < best_dist:
            best_dist = dist
            best = (pr, pg, pb)
    return best


def _find_nearest_index(r: int, g: int, b: int, pal_colors: list[tuple[int, int, int]]) -> int:
    best_idx = 1
    best_dist = float("inf")
    for i, (pr, pg, pb) in enumerate(pal_colors):
        dist = (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2
        if dist < best_dist:
            best_dist = dist
            best_idx = i + 1
    return best_idx
