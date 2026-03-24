# HR Bot - Claude Code 作業ガイド

## プロジェクト概要

Discord Bot。`/hr` でランダムな区切り線を投稿、`/addhr` で登録、サーバーごとにリストを管理する。

## 技術スタック

- **言語**: Python 3.11（uvで管理）
- **Discordライブラリ**: discord.py 2.x
- **DB**: SQLite + aiosqlite（非同期）
- **ホスティング**: Fly.io（東京リージョン `nrt`、アプリ名 `hr-bot`）
- **永続ボリューム**: `/data/hr.db`（Fly.io Volume `hr_data`）

## ファイル構成

```
src/
├── main.py       # Bot起動・Cog読み込み・スラッシュコマンド同期
├── db.py         # SQLite CRUD（add_hr / get_random_hr / list_hr / remove_hr）
└── cogs/
    └── hr.py     # /hr /addhr /listhr /removehr コマンド
```

## よく使うコマンド

```bash
# ローカル起動
uv run python -m src.main

# 依存パッケージ追加
uv add <package>

# Fly.ioへデプロイ
fly deploy

# 本番ログ確認
fly logs

# シークレット更新
fly secrets set DISCORD_TOKEN=<token>
```

## 環境変数

| 変数名 | 説明 | ローカル | 本番 |
|--------|------|----------|------|
| `DISCORD_TOKEN` | BotトークN（Developer Portal） | `.env` | `fly secrets` |
| `DB_PATH` | SQLiteファイルパス | `./hr.db` | `/data/hr.db` |

## DB スキーマ

```sql
CREATE TABLE hr_entries (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    guild_id   TEXT     NOT NULL,
    text       TEXT     NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(guild_id, text)
);
```

## コーディング規約

- コメントはすべて日本語で記述する
- DB操作はすべて `src/db.py` に集約する
- コマンドを追加する場合は `src/cogs/` に新しいCogファイルを作成し、`src/main.py` の `COGS` リストに追記する
- ユーザーへの応答は原則 `ephemeral=True`（本人のみ表示）にする。ただし `/hr` のような全員に見せる投稿は除く

## デプロイ時の注意

- `fly launch` を再実行すると `fly.toml` が上書きされる。`[http_service]` セクションが追加されてしまうため、実行後は削除すること
- BotはワーカープロセスのためHTTPポートは不要

## GitHub

リポジトリ: https://github.com/void2610/hr-bot
