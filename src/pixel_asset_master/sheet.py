"""Sprite sheet packing command."""

import json
import sys
from pathlib import Path

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:  # pragma: no cover
    HAS_PIL = False


def cmd_sheet(project_path_str: str, by_category: bool = True) -> None:
    """Pack individual PNG sprites into sprite sheets with a manifest."""
    if not HAS_PIL:
        print("[ERROR] Pillow required: pip install Pillow")
        sys.exit(1)

    project_path = Path(project_path_str)
    assets_dir = project_path / "assets"
    sheets_dir = project_path / "sheets"

    if not assets_dir.exists():
        print("[ERROR] No assets directory")
        return

    sheets_dir.mkdir(parents=True, exist_ok=True)
    manifest = {"sheets": []}

    categories = sorted(d.name for d in assets_dir.iterdir() if d.is_dir())

    for cat in categories:
        cat_dir = assets_dir / cat
        pngs = sorted(cat_dir.glob("*.png"))

        if not pngs:
            continue

        sizes: dict[str, list[Path]] = {}
        for png in pngs:
            img = Image.open(png)
            key = f"{img.width}x{img.height}"
            sizes.setdefault(key, []).append(png)

        for size_key, files in sizes.items():
            w, h = map(int, size_key.split("x"))

            if by_category:
                anim_groups = _group_by_animation(files)
                for anim_name, anim_files in anim_groups.items():
                    sheet_name = f"{cat}_{anim_name}_{size_key}.png"
                    _create_sheet(
                        sheets_dir / sheet_name, anim_files, w, h, manifest, cat, anim_name
                    )
            else:
                sheet_name = f"{cat}_{size_key}.png"
                _create_sheet(sheets_dir / sheet_name, files, w, h, manifest, cat, "all")

    manifest_path = sheets_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[OK] Generated {len(manifest['sheets'])} sheet(s), manifest saved")


def _group_by_animation(files: list[Path]) -> dict[str, list[Path]]:
    """Group animation frames by base animation name."""
    groups: dict[str, list[Path]] = {}
    for f in files:
        stem = f.stem
        parts = stem.rsplit("_", 1)
        if len(parts) == 2 and parts[1].isdigit():
            anim_name = parts[0]
        else:
            anim_name = stem

        groups.setdefault(anim_name, []).append(f)

    return groups


def _create_sheet(
    sheet_path: Path,
    files: list[Path],
    tile_w: int,
    tile_h: int,
    manifest: dict,
    category: str,
    anim_name: str,
) -> None:
    n = len(files)
    cols = min(n, 16)
    rows = (n + cols - 1) // cols

    sheet = Image.new("RGBA", (cols * tile_w, rows * tile_h), (0, 0, 0, 0))

    for i, f in enumerate(files):
        img = Image.open(f).convert("RGBA")
        col = i % cols
        row = i // cols
        sheet.paste(img, (col * tile_w, row * tile_h))

    sheet.save(sheet_path, "PNG")

    manifest["sheets"].append({
        "file": sheet_path.name,
        "category": category,
        "animation": anim_name,
        "tile_size": {"width": tile_w, "height": tile_h},
        "columns": cols,
        "rows": rows,
        "frame_count": n,
        "frames": [f.stem for f in files],
    })

    print(f"  Packed: {sheet_path.name} ({n} frames, {cols}x{rows})")
