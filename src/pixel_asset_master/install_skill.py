"""Install the bundled pam Agent Skill to the local skills directory."""

import shutil
import sys
from pathlib import Path


def get_skill_source_path() -> Path:
    """Return the path to the bundled skills/pam directory inside the package."""
    return Path(__file__).parent / "skills" / "pam"


def cmd_install_skills(target: str | None = None, dry_run: bool = False) -> bool:
    """Install the bundled pam skill to ``target`` (default ``~/.agents/skills/pam``).

    Args:
        target: Destination directory. Defaults to ``~/.agents/skills/pam``.
        dry_run: If True, only print what would happen without copying.

    Returns:
        True on success, False on failure.
    """
    src = get_skill_source_path()
    if not src.exists():
        print(f"Skill source not found: {src}", file=sys.stderr)
        return False

    dst = Path(target).expanduser() if target else Path.home() / ".agents" / "skills" / "pam"

    if dry_run:
        print(f"[dry-run] Would install skill from {src} to {dst}")
        return True

    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dst)
    print(f"Installed pam skill to {dst}")
    return True
