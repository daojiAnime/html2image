# Stage 1: 构建阶段
FROM python:3.12-slim AS builder

WORKDIR /app

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# 安装依赖
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# 复制源码并安装项目（包括 entry point）
COPY src ./src
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev

# 安装 Playwright Chromium（指定路径便于复制）
ENV PLAYWRIGHT_BROWSERS_PATH=/app/browsers
RUN .venv/bin/playwright install chromium && \
    # 清理不必要的文件
    rm -rf /app/browsers/*/chrome-linux/locales/*.pak && \
    find /app/browsers -name "*.debug" -delete


# Stage 2: 运行时阶段
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Shanghai
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app
ENV PLAYWRIGHT_BROWSERS_PATH=/app/browsers

# 安装运行时依赖（单层合并）
RUN sed -i 's|deb.debian.org|mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    # Chromium 最小运行时依赖
    libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
    libcups2 libdrm2 libdbus-1-3 libxkbcommon0 \
    libatspi2.0-0 libxcomposite1 libxdamage1 libxfixes3 \
    libxrandr2 libgbm1 libasound2 \
    # 精简中文字体（比 noto-cjk 小很多）
    fonts-wqy-zenhei \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# 从构建阶段复制
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/browsers /app/browsers
COPY --from=builder /app/src /app/src
COPY --from=builder /app/pyproject.toml /app/

ENTRYPOINT ["html2image"]
CMD ["--help"]
