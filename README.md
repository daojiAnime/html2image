# HTML2Image

🖼️ **HTML 转高清图片工具** - 支持高DPI渲染，确保文字清晰

[![PyPI version](https://badge.fury.io/py/html2image-cli.svg)](https://badge.fury.io/py/html2image-cli)
[![Python](https://img.shields.io/pypi/pyversions/html2image-cli.svg)](https://pypi.org/project/html2image-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

```
 _   _ _____ __  __ _     ____  ___
| | | |_   _|  \/  | |   |___ \|_ _|_ __ ___   __ _  __ _  ___
| |_| | | | | |\/| | |     __) || || '_ ` _ \ / _` |/ _` |/ _ \
|  _  | | | | |  | | |___ / __/ | || | | | | | (_| | (_| |  __/
|_| |_| |_| |_|  |_|_____|_____|___|_| |_| |_|\__,_|\__, |\___|
                                                   |___/
```

## ✨ 特性

- 🎯 **高清渲染** - 支持 2x/3x DPI 缩放，确保文字锐利清晰
- 🚀 **批量处理** - 一键转换整个目录的 HTML 文件
- 🎨 **美观 CLI** - 使用 Rich 实现的精美命令行界面
- ⚡ **字体优化** - 自动等待字体和图标加载完成
- 📦 **开箱即用** - 基于 Playwright，无需额外配置

## 📦 安装

```bash
# 使用 pip 安装
pip install html2image-cli

# 使用 uv 安装（推荐）
uv pip install html2image-cli

# 安装 Playwright 浏览器（首次使用需要）
playwright install chromium
```

## 🚀 快速开始

### 渲染单个文件

```bash
# 基础用法（2x 高清）
html2image render page.html

# 指定输出路径
html2image render page.html -o output.png

# 3x 超清渲染
html2image render page.html --scale 3

# 输出 JPEG 格式
html2image render page.html --format jpeg --quality 95

# 自定义视口宽度
html2image render page.html --width 1400
```

### 批量渲染

```bash
# 渲染目录下所有 HTML 文件
html2image batch ./reports

# 指定输出目录
html2image batch ./pages -o ./images

# 批量渲染为 JPEG
html2image batch ./docs --format jpeg --quality 90
```

## 📖 命令参考

### `html2image render`

渲染单个 HTML 文件为高清图片

| 参数 | 短选项 | 默认值 | 说明 |
|------|--------|--------|------|
| `INPUT_PATH` | - | (必填) | 输入的 HTML 文件路径 |
| `--output` | `-o` | 同名文件 | 输出图片路径 |
| `--width` | `-w` | 1200 | 视口宽度（像素） |
| `--scale` | `-s` | 2.0 | DPI 缩放比例（2=高清，3=超清） |
| `--format` | `-f` | png | 输出格式（png/jpeg） |
| `--quality` | `-q` | 90 | JPEG 质量（0-100） |
| `--wait` | - | 500 | 额外等待渲染时间（毫秒） |

### `html2image batch`

批量渲染目录下所有 HTML 文件

| 参数 | 短选项 | 默认值 | 说明 |
|------|--------|--------|------|
| `DIRECTORY` | - | (必填) | 包含 HTML 文件的目录 |
| `--output` | `-o` | 同目录 | 输出目录 |
| `--width` | `-w` | 1200 | 视口宽度（像素） |
| `--scale` | `-s` | 2.0 | DPI 缩放比例 |
| `--format` | `-f` | png | 输出格式 |
| `--quality` | `-q` | 90 | JPEG 质量 |
| `--wait` | - | 500 | 额外等待时间（毫秒） |

### 全局选项

| 参数 | 短选项 | 说明 |
|------|--------|------|
| `--help` | `-h` | 显示帮助信息 |
| `--version` | `-V` | 显示版本信息 |

## 🐍 Python API

```python
from pathlib import Path
from html2image import render_html_to_image, batch_render

# 渲染单个文件
result = render_html_to_image(
    input_path=Path("page.html"),
    output_path=Path("output.png"),
    width=1200,
    scale=2.0,
)
print(f"生成: {result.output_path}, 尺寸: {result.width}x{result.height}")

# 批量渲染
results = batch_render(
    directory=Path("./reports"),
    output_dir=Path("./images"),
    scale=2.0,
)
print(f"共处理 {len(results)} 个文件")
```

## 🎯 最佳实践

### 信息图/报告渲染

对于包含大量文字的信息图或报告，推荐使用以下配置：

```bash
# 推荐配置：2x 缩放，1200px 宽度
html2image render infographic.html --scale 2 --width 1200

# 超高清打印：3x 缩放
html2image render report.html --scale 3 --width 1400
```

### 减小文件大小

如果需要控制文件大小，可以使用 JPEG 格式：

```bash
html2image render page.html --format jpeg --quality 85
```

### 处理特殊字体

如果页面使用了 Web 字体（如 Google Fonts），可以增加等待时间：

```bash
html2image render page.html --wait 1000
```

## 🔧 技术细节

- 使用 [Playwright](https://playwright.dev/) Chromium 进行渲染
- 通过 `deviceScaleFactor` 实现高 DPI 输出
- 自动等待 `document.fonts.ready` 确保字体加载
- 支持 [Lucide Icons](https://lucide.dev/) 等图标库的自动渲染

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件
