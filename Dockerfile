FROM python:3.11-slim

# 作業ディレクトリを設定
WORKDIR /app

# uvをインストール
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 依存関係ファイルを先にコピー（キャッシュ活用）
COPY pyproject.toml uv.lock ./

# 依存パッケージをインストール（仮想環境なし・システムにインストール）
RUN uv sync --frozen --no-dev --no-install-project

# ソースコードをコピー
COPY src/ ./src/

# Botを起動
CMD ["uv", "run", "python", "-m", "src.main"]
