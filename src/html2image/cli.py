"""HTML to Image CLI - 使用 Typer + Rich 实现的命令行工具"""

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path
from typing import TYPE_CHECKING, Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Table
from rich.text import Text

from html2image.render import batch_render, render_html_to_image

if TYPE_CHECKING:
    pass

__version__ = version("html2image-cli")
console = Console()

# ASCII Art Logo
LOGO = r"""
 _   _ _____ __  __ _     ____  ___
| | | |_   _|  \/  | |   |___ \|_ _|_ __ ___   __ _  __ _  ___
| |_| | | | | |\/| | |     __) || || '_ ` _ \ / _` |/ _` |/ _ \
|  _  | | | | |  | | |___ / __/ | || | | | | | (_| | (_| |  __/
|_| |_| |_| |_|  |_|_____|_____|___|_| |_| |_|\__,_|\__, |\___|
                                                   |___/
"""


def gradient_text(text: str, colors: list[str] | None = None) -> Text:
    """创建渐变色文本"""
    from rich.color import Color

    if colors is None:
        # 蓝紫渐变：专业科技感
        colors = ["#60a5fa", "#818cf8", "#a78bfa", "#c084fc"]

    result = Text()
    lines = text.split("\n")
    total_chars = sum(len(line) for line in lines)
    char_idx = 0

    for line in lines:
        for char in line:
            progress = char_idx / max(total_chars - 1, 1)
            color_pos = progress * (len(colors) - 1)
            idx1 = int(color_pos)
            idx2 = min(idx1 + 1, len(colors) - 1)
            blend = color_pos - idx1

            c1 = Color.parse(colors[idx1])
            c2 = Color.parse(colors[idx2])
            if c1.triplet and c2.triplet:
                r = int(c1.triplet.red * (1 - blend) + c2.triplet.red * blend)
                g = int(c1.triplet.green * (1 - blend) + c2.triplet.green * blend)
                b = int(c1.triplet.blue * (1 - blend) + c2.triplet.blue * blend)
                result.append(char, style=f"bold rgb({r},{g},{b})")
            else:
                result.append(char, style=f"bold {colors[idx1]}")
            char_idx += 1
        result.append("\n")

    return result


def print_success(message: str) -> None:
    """打印成功信息"""
    console.print(f"[bold green]✓[/] {message}")


def print_error(message: str) -> None:
    """打印错误信息"""
    console.print(f"[bold red]✗[/] {message}")


def print_info(message: str) -> None:
    """打印提示信息"""
    console.print(f"[bold blue]→[/] {message}")


def print_config_table(width: int, scale: float, fmt: str, quality: int) -> None:
    """打印配置表格"""
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Key", style="dim")
    table.add_column("Value", style="cyan bold")

    table.add_row("视口宽度", f"{width}px")
    table.add_row("缩放比例", f"{scale}x → 输出 {int(width * scale)}px")
    table.add_row("输出格式", fmt.upper())
    if fmt == "jpeg":
        table.add_row("JPEG质量", f"{quality}")

    console.print(Panel(table, title="[bold]渲染配置[/]", border_style="blue"))


app = typer.Typer(
    name="html2image",
    help="🖼️  [bold cyan]HTML 转高清图片工具[/] - 支持高DPI渲染，确保文字清晰",
    context_settings={"help_option_names": ["-h", "--help"]},
    rich_markup_mode="rich",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """版本回调"""
    if value:
        console.print(gradient_text(LOGO))
        console.print(f"[dim]Version:[/] [bold cyan]{__version__}[/]")
        console.print("[dim]Author:[/]  [bold]daoji[/]")
        console.print("[dim]GitHub:[/]  [link=https://github.com/nicepkg/html2image]https://github.com/nicepkg/html2image[/link]")
        raise typer.Exit()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    _version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="显示版本信息",
        ),
    ] = False,
) -> None:
    """🖼️  [bold cyan]HTML 转高清图片工具[/] - 支持高DPI渲染，确保文字清晰"""
    if ctx.invoked_subcommand is None:
        console.print(gradient_text(LOGO))
        console.print(ctx.get_help())


@app.command("render")
def render_command(
    input_path: Annotated[
        Path,
        typer.Argument(
            help="输入的 HTML 文件路径",
            exists=True,
            readable=True,
        ),
    ],
    output: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help="输出图片路径（默认与输入同名）",
            rich_help_panel="输出选项",
        ),
    ] = None,
    width: Annotated[
        int,
        typer.Option(
            "-w",
            "--width",
            help="视口宽度（像素）",
            rich_help_panel="渲染选项",
        ),
    ] = 1200,
    scale: Annotated[
        float,
        typer.Option(
            "-s",
            "--scale",
            help="DPI缩放比例（2=高清，3=超清）",
            rich_help_panel="渲染选项",
        ),
    ] = 2.0,
    fmt: Annotated[
        str,
        typer.Option(
            "-f",
            "--format",
            help="输出格式",
            rich_help_panel="输出选项",
        ),
    ] = "png",
    quality: Annotated[
        int,
        typer.Option(
            "-q",
            "--quality",
            help="JPEG质量（0-100）",
            rich_help_panel="输出选项",
            min=0,
            max=100,
        ),
    ] = 90,
    wait: Annotated[
        int,
        typer.Option(
            "--wait",
            help="额外等待渲染时间（毫秒）",
            rich_help_panel="渲染选项",
        ),
    ] = 500,
) -> None:
    """
    渲染单个 [green]HTML[/] 文件为高清图片

    \b
    示例:
      html2image render page.html
      html2image render page.html -o output.png --scale 3
      html2image render page.html --format jpeg --quality 95
    """
    # 验证格式
    if fmt not in ("png", "jpeg"):
        print_error(f"不支持的格式: {fmt}，请使用 png 或 jpeg")
        raise typer.Exit(1)

    # 验证文件类型
    if input_path.suffix.lower() not in (".html", ".htm"):
        print_error("输入文件必须是 .html 或 .htm 格式")
        raise typer.Exit(1)

    # 确定输出路径
    output_path = output or input_path.with_suffix(f".{fmt}")

    console.print()
    console.print(gradient_text(LOGO))
    print_config_table(width, scale, fmt, quality)
    console.print()

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]渲染 {input_path.name}...", total=100)

            progress.update(task, advance=20, description="[cyan]启动浏览器...")
            result = render_html_to_image(
                input_path=input_path,
                output_path=output_path,
                width=width,
                scale=scale,
                fmt=fmt,
                quality=quality,
                wait_ms=wait,
            )
            progress.update(task, advance=80, description="[green]渲染完成")

        console.print()
        print_success(f"已生成: [bold]{result.output_path.name}[/]")
        print_info(f"尺寸: [cyan]{result.width}x{result.height}[/] px")
        print_info(f"大小: [cyan]{result.size_mb:.2f}[/] MB")
        print_info(f"路径: [dim]{result.output_path}[/]")

    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
    except Exception as e:
        print_error(f"渲染失败: {e}")
        raise typer.Exit(1) from None


@app.command("batch")
def batch_command(
    directory: Annotated[
        Path,
        typer.Argument(
            help="包含 HTML 文件的目录",
            exists=True,
            file_okay=False,
            dir_okay=True,
        ),
    ],
    output_dir: Annotated[
        Path | None,
        typer.Option(
            "-o",
            "--output",
            help="输出目录（默认与输入同目录）",
            rich_help_panel="输出选项",
        ),
    ] = None,
    width: Annotated[
        int,
        typer.Option(
            "-w",
            "--width",
            help="视口宽度（像素）",
            rich_help_panel="渲染选项",
        ),
    ] = 1200,
    scale: Annotated[
        float,
        typer.Option(
            "-s",
            "--scale",
            help="DPI缩放比例（2=高清，3=超清）",
            rich_help_panel="渲染选项",
        ),
    ] = 2.0,
    fmt: Annotated[
        str,
        typer.Option(
            "-f",
            "--format",
            help="输出格式",
            rich_help_panel="输出选项",
        ),
    ] = "png",
    quality: Annotated[
        int,
        typer.Option(
            "-q",
            "--quality",
            help="JPEG质量（0-100）",
            rich_help_panel="输出选项",
            min=0,
            max=100,
        ),
    ] = 90,
    wait: Annotated[
        int,
        typer.Option(
            "--wait",
            help="额外等待渲染时间（毫秒）",
            rich_help_panel="渲染选项",
        ),
    ] = 500,
) -> None:
    """
    批量渲染目录下所有 [green]HTML[/] 文件

    \b
    示例:
      html2image batch ./reports
      html2image batch ./pages -o ./images --scale 3
      html2image batch ./docs --format jpeg --quality 90
    """
    # 验证格式
    if fmt not in ("png", "jpeg"):
        print_error(f"不支持的格式: {fmt}，请使用 png 或 jpeg")
        raise typer.Exit(1)

    console.print()
    console.print(gradient_text(LOGO))
    print_config_table(width, scale, fmt, quality)
    console.print()

    try:
        results = batch_render(
            directory=directory,
            output_dir=output_dir,
            width=width,
            scale=scale,
            fmt=fmt,
            quality=quality,
            wait_ms=wait,
            console=console,
        )

        console.print()
        if results:
            # 显示结果汇总表
            table = Table(title="[bold]渲染结果汇总[/]", show_lines=True)
            table.add_column("文件", style="cyan")
            table.add_column("尺寸", justify="right")
            table.add_column("大小", justify="right", style="green")
            table.add_column("状态", justify="center")

            for r in results:
                table.add_row(
                    r.output_path.name,
                    f"{r.width}x{r.height}",
                    f"{r.size_mb:.2f} MB",
                    "[green]✓[/]",
                )

            console.print(table)
            console.print()
            print_success(f"共处理 [bold]{len(results)}[/] 个文件")
        else:
            print_info("没有找到 HTML 文件")

    except FileNotFoundError as e:
        print_error(str(e))
        raise typer.Exit(1) from None
    except Exception as e:
        print_error(f"批量处理失败: {e}")
        raise typer.Exit(1) from None


def cli_main() -> None:
    """CLI 入口点"""
    app()


if __name__ == "__main__":
    cli_main()
