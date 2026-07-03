# Project Structure

本文档记录 `pixel-asset-master-skills` 的 GitHub 仓库结构约定。

## 顶层结构

```text
.
├── README.md
├── README_CN.md
├── LICENSE
├── CONTRIBUTING.md
├── CODE_OF_CONDUCT.md
├── SECURITY.md
├── pyproject.toml
├── uv.lock
├── src/
│   └── pixel_asset_master/       # 可安装的 Python CLI 包
├── docs/
│   └── PROJECT_STRUCTURE.md
├── index.html
├── projects/
│   ├── README.md
│   └── examples/
│       └── mario_32x32_20260502/
└── skills/
    └── pixel-asset-master/
```

## Skill 结构

```text
skills/pixel-asset-master/
├── SKILL.md
├── references/
│   ├── executor-pixel.md
│   ├── shared-standards.md
│   └── strategist.md
├── scripts/
│   └── README.md                 # CLI 命令参考
├── templates/
│   ├── design_spec_reference.md
│   ├── spec_lock_reference.md
│   ├── palettes/
│   │   └── palettes_index.json
│   ├── sizes/
│   │   └── sizes_index.json
│   └── sprites/
│       └── sprites_index.json
└── workflows/
    ├── batch-animate.md
    └── create-palette.md
```

## 目录职责

- **`skills/pixel-asset-master/SKILL.md`**：AI skill 的主入口，定义完整像素素材生产流水线。
- **`references/`**：拆分角色职责和执行标准，避免主入口过长。
- **`src/pixel_asset_master/`**：可安装的 Python CLI 包，提供 `pam` 统一命令行入口（项目初始化、调色板分析、素材校验、后处理、精灵图打包）。
- **`scripts/`**：CLI 命令参考文档，不再包含独立的 `.py` 脚本。
- **`templates/`**：调色板、尺寸、精灵布局和规格文件模板。
- **`workflows/`**：可独立调用的补充流程。
- **`docs/`**：仓库维护文档。

## 生成内容边界

以下内容属于本地运行产物，不建议提交 Git：

- `projects/*`（但保留 `projects/README.md` 和 `projects/examples/` 作为示例）
- `exports/`
- 打包文件，例如 `*.zip`、`*.tar.gz`
- 临时文件，例如 `*.tmp`、`*.bak`
- 本地环境文件，例如 `.env`、`.venv/`

## 架构整理记录

本次整理将项目明确为“仓库级文档 + 单 skill 包 + 独立 CLI 包”的形式：

- 根目录保留 GitHub 展示、协作文件，以及可独立安装的 Python CLI 包（`pyproject.toml`、`uv.lock`、`src/pixel_asset_master/`）。
- skill 的 AI workflow 定义仍保留在 `skills/pixel-asset-master/`，但其可执行主体已迁移到根目录的 `src/pixel_asset_master/`，通过 `pam` 统一调用。
- 依赖管理从 `pip install -r requirements.txt` 迁移到 [uv](https://docs.astral.sh/uv/)，支持 `uv tool install .` 全局安装 `pam` 命令。
- 生成项目统一输出到根目录 `projects/`，并由 `.gitignore` 排除。
- 根 `README.md` 使用产品页式结构，包含徽章、语言入口、Quick Start、Documentation 表和贡献入口。
- 新增 `README_CN.md`，与英文 README 保持同等导航能力。
- 新增 `SECURITY.md` 与 `CODE_OF_CONDUCT.md`，补齐开源协作文件。
- 新增 `index.html` 作为项目展示页，含樱花树序列帧动画、古风小生多动作精灵图动画和全页花瓣粒子。
- `projects/examples/` 保留示例项目（含 design_spec、spec_lock、精灵图和 manifest），供用户参考。
- `sizes_index.json` 扩展至 2048x2048，新增 High-Res Pixel 和 Cinematic Pixel 风格。
- `sprites_index.json` 人物模板新增 `facing_directions`、`common_actions`、`recommended_sizes`、`actions` 字段。
- `SKILL.md` Step 4 六项确认第 6 项扩展为动画详细确认（面朝方向 + 动作列表 + 每动作帧数）。
- `README.md` 与 `README_CN.md` 的 Quick Start 拆分为“无参考图片”和“有参考图片”两种生成方式，并新增 Cursor、Trae、Windsurf 等 AI Coding IDE 的打开与使用说明。
