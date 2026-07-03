# Pixel Asset Master - CLI Reference

## Overview

Pixel Asset Master now ships as a single installable CLI, `pam`.

Install from the repository root:

```bash
uv tool install .
```

Or run without installing:

```bash
uv run pam --help
```

## Global options

| Option | Description |
|--------|-------------|
| `--root <path>` | Workspace root directory (default: current directory) |
| `--version` | Show version |

The `--root` option and the `PAM_PROJECTS_ROOT` environment variable control where `pam init` creates the `projects/` directory.

## Commands

### `pam init`

Initialize a new pixel art asset project.

```bash
pam init <name> --size 32x32 --palette DB32
```

### `pam import-sources`

Import reference images into a project.

```bash
pam import-sources <project_path> <files...> [--move]
```

### `pam validate-project`

Validate project structure (required files and directories).

```bash
pam validate-project <project_path>
```

### `pam validate-assets`

Validate pixel art assets against `spec_lock.md`.

```bash
pam validate-assets <project_path>
```

Checks: palette compliance, color budget, anti-aliasing, file format.

### `pam palette`

Palette extraction and validation.

```bash
# Extract palette from reference image
pam palette extract <image> --count 16

# Validate assets against project palette
pam palette validate <project_path>

# Calculate color distance
pam palette distance '#FF0000' '#00FF00'
```

### `pam finalize`

Post-process pixel art assets.

```bash
# Quantize colors to declared palette
pam finalize <project_path> --quantize

# Clean stray isolated pixels
pam finalize <project_path> --clean

# Convert to indexed PNG
pam finalize <project_path> --index

# Run all steps
pam finalize <project_path> --all
```

### `pam sheet`

Pack individual PNGs into sprite sheets.

```bash
pam sheet <project_path> --by-category
```

Output: sprite sheet PNGs + `manifest.json` with frame metadata.

## Dependencies

- **Pillow**: Required for image processing (managed by uv via `pyproject.toml`)
- **Python 3.8+**: Minimum version
