"""
HTML2Image - HTML 转高清图片工具

支持高DPI渲染、字体等待、批量处理，确保文字清晰。
"""

from __future__ import annotations

from html2image.render import RenderResult, batch_render, render_html_to_image

__all__ = [
    "RenderResult",
    "batch_render",
    "render_html_to_image",
]
