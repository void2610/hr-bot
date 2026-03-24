# HR Bot

Discordの会話に区切り線（HR: Horizontal Rule）を投稿できるBotです。
サーバーごとに区切り線リストを管理し、スラッシュコマンドで呼び出せます。

## コマンド一覧

| コマンド | 説明 |
|----------|------|
| `/hr` | 登録済みの区切り線をランダムに投稿 |
| `/addhr <text>` | 区切り線を登録（200文字以内・重複不可） |
| `/listhr` | 登録済み一覧をID付きで表示（自分のみ表示） |
| `/removehr <entry_id>` | 指定IDの区切り線を削除 |

## 技術スタック

| 役割 | 技術 |
|------|------|
| 言語 | Python 3.11 |
| Discordライブラリ | discord.py 2.x |
| データベース | SQLite（aiosqlite） |
| ホスティング | Fly.io（東京リージョン） |
| 永続ストレージ | Fly.io Volume（/data/hr.db） |

## ディレクトリ構成

```
hr-bot/
├── src/
│   ├── main.py          # Bot起動・初期化
│   ├── db.py            # SQLite CRUD
│   └── cogs/
│       └── hr.py        # スラッシュコマンド定義
├── DESIGN.md            # 詳細設計ドキュメント
├── Dockerfile           # コンテナ定義
├── fly.toml             # Fly.io設定
├── pyproject.toml       # Pythonプロジェクト設定（uv）
├── .env.example         # 環境変数テンプレート
└── .gitignore
```

## ローカル開発

### 前提条件

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)

### セットアップ

```bash
# 依存パッケージのインストール
uv sync

# 環境変数の設定
cp .env.example .env
# .envを編集してDISCORD_TOKENを設定

# 起動
uv run python -m src.main
```

### Discord Developer Portal の設定

1. [Discord Developer Portal](https://discord.com/developers/applications) でアプリケーションを作成
2. **Bot** メニューからトークンを取得し `.env` に設定
3. **OAuth2 > URL Generator** でスコープ `bot` + `applications.commands`、権限 `Send Messages` を選択してInvite URLを生成
4. URLをブラウザで開いてBotをサーバーに招待

## デプロイ（Fly.io）

### 初回デプロイ

```bash
# flyctlのインストール
brew install flyctl

# ログイン
fly auth login

# アプリ作成（デプロイはしない）
fly launch --no-deploy --yes

# 永続ボリューム作成
fly volumes create hr_data --region nrt --size 1

# シークレット登録
fly secrets set DISCORD_TOKEN=<your_token> DB_PATH=/data/hr.db

# デプロイ
fly deploy
```

### 更新デプロイ

```bash
fly deploy
```

### ログ確認

```bash
fly logs
```

### Fly.io 無料枠

| リソース | 使用量 | 無料枠 |
|----------|--------|--------|
| VM | shared-cpu-1x / 256MB × 1台 | 3台まで無料 |
| ボリューム | 1GB | 3GBまで無料 |
