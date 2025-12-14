"""HTML 渲染核心模块 - 使用 Playwright 实现高清截图"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

from playwright.sync_api import sync_playwright

if TYPE_CHECKING:
    from rich.console import Console


@dataclass
class RenderResult:
    """渲染结果"""

    output_path: Path
    width: int
    height: int
    size_mb: float


def render_html_to_image(
    input_path: Path,
    output_path: Path,
    width: int = 1200,
    scale: float = 2.0,
    fmt: str = "png",
    quality: int = 90,
    wait_ms: int = 500,
) -> RenderResult:
    """
    将HTML文件渲染为高清图片

    Args:
        input_path: 输入HTML文件路径
        output_path: 输出图片路径
        width: 视口宽度
        scale: DPI缩放比例（2=2x高清，3=3x超清）
        fmt: 输出格式 png/jpeg
        quality: JPEG质量 0-100
        wait_ms: 额外等待时间(毫秒)

    Returns:
        RenderResult: 渲染结果信息
    """
    input_path = input_path.resolve()
    output_path = output_path.resolve()

    if not input_path.exists():
        raise FileNotFoundError(f"文件不存在: {input_path}")

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        # 启动浏览器，优化字体渲染
        browser = p.chromium.launch(
            args=[
                "--font-render-hinting=none",
                "--disable-lcd-text",
                "--disable-font-subpixel-positioning",
            ]
        )

        # 创建上下文，设置高DPI
        context = browser.new_context(
            viewport={"width": width, "height": 800},
            device_scale_factor=scale,
        )

        page = context.new_page()

        # 导航到HTML文件
        page.goto(f"file://{input_path}", wait_until="networkidle", timeout=30000)

        # 等待字体加载完成
        page.evaluate("() => document.fonts.ready")

        # 等待所有图片加载
        page.evaluate(
            """() => {
            const images = Array.from(document.images);
            return Promise.all(images.map(img => {
                if (img.complete) return Promise.resolve();
                return new Promise((resolve) => {
                    img.addEventListener('load', resolve);
                    img.addEventListener('error', resolve);
                });
            }));
        }"""
        )

        # 等待Lucide图标渲染
        page.evaluate(
            """() => {
            if (typeof lucide !== 'undefined' && lucide.createIcons) {
                lucide.createIcons();
            }
        }"""
        )

        # 额外等待确保渲染完成
        page.wait_for_timeout(wait_ms)

        # 获取页面实际高度
        body_height = page.evaluate(
            """() => {
            return Math.max(
                document.body.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.clientHeight,
                document.documentElement.scrollHeight,
                document.documentElement.offsetHeight
            );
        }"""
        )

        # 设置视口高度为页面实际高度
        page.set_viewport_size({"width": width, "height": body_height})

        # 等待布局稳定
        page.wait_for_timeout(200)

        # 截图配置
        screenshot_options: dict = {
            "path": str(output_path),
            "full_page": True,
            "type": fmt,
        }

        if fmt == "jpeg":
            screenshot_options["quality"] = quality

        page.screenshot(**screenshot_options)

        browser.close()

    # 获取输出文件信息
    size_mb = output_path.stat().st_size / 1024 / 1024
    actual_width = int(width * scale)
    actual_height = int(body_height * scale)

    return RenderResult(
        output_path=output_path,
        width=actual_width,
        height=actual_height,
        size_mb=size_mb,
    )


def batch_render(
    directory: Path,
    output_dir: Path | None = None,
    width: int = 1200,
    scale: float = 2.0,
    fmt: str = "png",
    quality: int = 90,
    wait_ms: int = 500,
    console: Console | None = None,
) -> list[RenderResult]:
    """
    批量处理目录下所有HTML文件

    Args:
        directory: 目录路径
        output_dir: 输出目录（默认与输入同目录）
        width: 视口宽度
        scale: DPI缩放比例
        fmt: 输出格式
        quality: JPEG质量
        wait_ms: 额外等待时间
        console: Rich Console 实例

    Returns:
        生成的 RenderResult 列表
    """
    from rich.progress import (
        BarColumn,
        Progress,
        SpinnerColumn,
        TaskProgressColumn,
        TextColumn,
        TimeElapsedColumn,
    )

    directory = directory.resolve()
    output_dir = (output_dir or directory).resolve()

    if not directory.exists():
        raise FileNotFoundError(f"目录不存在: {directory}")

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    html_files = list(directory.glob("*.html")) + list(directory.glob("*.htm"))

    if not html_files:
        return []

    results: list[RenderResult] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(
            f"[cyan]批量渲染 {len(html_files)} 个文件...", total=len(html_files)
        )

        for html_file in html_files:
            output_path = output_dir / f"{html_file.stem}.{fmt}"
            try:
                progress.update(task, description=f"[cyan]渲染 {html_file.name}...")
                result = render_html_to_image(
                    input_path=html_file,
                    output_path=output_path,
                    width=width,
                    scale=scale,
                    fmt=fmt,
                    quality=quality,
                    wait_ms=wait_ms,
                )
                results.append(result)
            except Exception as e:
                if console:
                    console.print(f"[red]✗[/] 处理失败: {html_file.name} - {e}")
            finally:
                progress.advance(task)

    return results
