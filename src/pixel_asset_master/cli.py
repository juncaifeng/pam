"""Unified CLI entry point for Pixel Asset Master."""

import argparse
import sys

from pixel_asset_master import __version__
from pixel_asset_master.common import resolve_root
from pixel_asset_master.finalize import cmd_clean, cmd_index, cmd_quantize
from pixel_asset_master.install_skill import cmd_install_skills
from pixel_asset_master.palette import cmd_distance, cmd_extract, cmd_validate as cmd_validate_palette
from pixel_asset_master.project import cmd_import_sources, cmd_init, cmd_validate_project
from pixel_asset_master.sheet import cmd_sheet
from pixel_asset_master.validate import cmd_validate_assets


def _add_root_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--root",
        default=None,
        help="Workspace root directory (default: current directory; override with PAM_PROJECTS_ROOT env var)",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pam",
        description="Pixel Asset Master — AI-driven 2D pixel game asset toolkit",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    _add_root_argument(parser)

    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── init ───────────────────────────────────────────────────────────────
    p_init = sub.add_parser("init", help="Initialize a new project")
    p_init.add_argument("project_name", help="Project name")
    p_init.add_argument("--size", default="32x32", help="Base sprite size (e.g. 32x32)")
    p_init.add_argument("--palette", default="DB32", help="Palette name (resolved from workspace palettes_index.json if available)")
    p_init.add_argument("--palette-file", default=None, help="Path to a JSON palette file")
    p_init.add_argument("--palette-colors", default=None, help="Comma-separated hex colors (e.g. '#FF0000,#00FF00')")

    # ── import-sources ─────────────────────────────────────────────────────
    p_import = sub.add_parser("import-sources", help="Import reference images into a project")
    p_import.add_argument("project_path", help="Project directory path")
    p_import.add_argument("files", nargs="+", help="Files to import")
    p_import.add_argument("--move", action="store_true", help="Move instead of copy")

    # ── validate-project ───────────────────────────────────────────────────
    p_validate = sub.add_parser("validate-project", help="Validate project structure")
    p_validate.add_argument("project_path", help="Project directory path")

    # ── validate-assets ────────────────────────────────────────────────────
    p_validate_assets = sub.add_parser("validate-assets", help="Validate pixel art assets against spec_lock")
    p_validate_assets.add_argument("project_path", help="Project directory path")
    p_validate_assets.add_argument("--strict", action="store_true", default=True, help="Treat anti-aliasing/semi-transparent pixels as errors (default)")
    p_validate_assets.add_argument("--no-strict", action="store_true", help="Treat anti-aliasing/semi-transparent pixels as warnings")

    # ── palette ────────────────────────────────────────────────────────────
    p_palette = sub.add_parser("palette", help="Palette extraction and validation")
    pal_sub = p_palette.add_subparsers(dest="palette_command", help="Palette commands")

    p_pal_extract = pal_sub.add_parser("extract", help="Extract palette from image")
    p_pal_extract.add_argument("image_path", help="Path to reference image")
    p_pal_extract.add_argument("--count", type=int, default=16, help="Number of colors")

    p_pal_validate = pal_sub.add_parser("validate", help="Validate assets against project palette")
    p_pal_validate.add_argument("project_path", help="Project directory path")

    p_pal_distance = pal_sub.add_parser("distance", help="Distance between two colors")
    p_pal_distance.add_argument("color1", help="First color (#RRGGBB)")
    p_pal_distance.add_argument("color2", help="Second color (#RRGGBB)")

    # ── finalize ───────────────────────────────────────────────────────────
    p_finalize = sub.add_parser("finalize", help="Post-process pixel art assets")
    p_finalize.add_argument("project_path", help="Project directory path")
    p_finalize.add_argument("--quantize", action="store_true", help="Quantize to declared palette")
    p_finalize.add_argument("--clean", action="store_true", help="Remove stray isolated pixels")
    p_finalize.add_argument("--index", action="store_true", help="Convert to indexed PNG")
    p_finalize.add_argument("--all", action="store_true", help="Run all steps")

    # ── sheet ──────────────────────────────────────────────────────────────
    p_sheet = sub.add_parser("sheet", help="Pack sprite sheets")
    p_sheet.add_argument("project_path", help="Project directory path")
    p_sheet.add_argument("--by-category", action="store_true", default=True, help="Pack by category/animation")

    # ── install-skills ─────────────────────────────────────────────────────
    p_install = sub.add_parser("install-skills", help="Install the bundled pam Agent Skill")
    p_install.add_argument("--target", default=None, help="Destination directory (default: ~/.agents/skills/pam)")
    p_install.add_argument("--dry-run", action="store_true", help="Print what would be installed without copying")

    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 1

    # Resolve root for commands that need it. Most commands use explicit project_path.
    _ = resolve_root(args.root)

    if args.command == "init":
        palette_colors = None
        if args.palette_colors:
            palette_colors = [c.strip() for c in args.palette_colors.split(",")]
        cmd_init(
            args.project_name,
            args.size,
            args.palette,
            palette_file=args.palette_file,
            palette_colors=palette_colors,
            root=args.root,
        )
        return 0

    if args.command == "import-sources":
        cmd_import_sources(args.project_path, args.files, move=args.move)
        return 0

    if args.command == "validate-project":
        ok = cmd_validate_project(args.project_path)
        return 0 if ok else 1

    if args.command == "validate-assets":
        strict = args.strict and not args.no_strict
        ok = cmd_validate_assets(args.project_path, strict=strict)
        return 0 if ok else 1

    if args.command == "palette":
        if args.palette_command == "extract":
            cmd_extract(args.image_path, count=args.count)
            return 0
        if args.palette_command == "validate":
            cmd_validate_palette(args.project_path)
            return 0
        if args.palette_command == "distance":
            cmd_distance(args.color1, args.color2)
            return 0
        p_palette.print_help()
        return 1

    if args.command == "finalize":
        if args.all or args.quantize:
            cmd_quantize(args.project_path)
        if args.all or args.clean:
            cmd_clean(args.project_path)
        if args.all or args.index:
            cmd_index(args.project_path)
        if not (args.quantize or args.clean or args.index or args.all):
            p_finalize.print_help()
            return 1
        return 0

    if args.command == "sheet":
        cmd_sheet(args.project_path, by_category=args.by_category)
        return 0

    if args.command == "install-skills":
        ok = cmd_install_skills(target=args.target, dry_run=args.dry_run)
        return 0 if ok else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
