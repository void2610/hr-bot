# HR Bot 設計ドキュメント

## 概要

Discordの会話に「区切り線（HR: Horizontal Rule）」を投稿できるBotです。
サーバーごとに区切り線リストを管理し、スラッシュコマンドで呼び出せます。

---

## 技術スタック

| 役割           | 技術                  | バージョン |
|----------------|-----------------------|------------|
| 言語           | Python                | 3.11+      |
| Discordライブラリ | discord.py          | 2.x        |
| データベース   | SQLite                | 標準ライブラリ（aiosqlite） |
| ホスティング   | Fly.io                | 無料枠     |
| 永続ストレージ | Fly.io Volume         | 3GB（無料） |

---

## コマンド仕様

### `/hr`
ランダムな区切り線を投稿します。

- **権限**: 全員
- **動作**: そのサーバーに登録された区切り線リストからランダムに1件選択して投稿
- **未登録時**: 「区切り線が登録されていません。`/addhr` で登録してください。」と返答

---

### `/addhr <text>`
区切り線を登録します。

- **権限**: 全員
- **引数**:
  - `text`（必須）: 登録する文字列（絵文字・スタンプ含む、最大200文字）
- **動作**: そのサーバーのリストに追加。同一文字列の重複登録は弾く
- **成功時**: 「✅ 区切り線を登録しました: `{text}`」と返答

---

### `/listhr`
登録済みの区切り線一覧を表示します。

- **権限**: 全員
- **動作**: そのサーバーに登録された全区切り線を番号付きで表示（ephemeral）
- **未登録時**: 「区切り線が登録されていません。」と返答

---

### `/removehr <number>`
区切り線を削除します。

- **権限**: 全員
- **引数**:
  - `number`（必須）: `/listhr` で表示された番号
- **動作**: 指定番号の区切り線を削除
- **成功時**: 「🗑️ 区切り線を削除しました: `{text}`」と返答

---

## データベース設計

### テーブル: `hr_entries`

| カラム名     | 型        | 制約                        | 説明                     |
|--------------|-----------|-----------------------------|--------------------------|
| `id`         | INTEGER   | PRIMARY KEY AUTOINCREMENT   | レコードID               |
| `guild_id`   | TEXT      | NOT NULL                    | DiscordサーバーID        |
| `text`       | TEXT      | NOT NULL                    | 区切り線の文字列         |
| `created_at` | DATETIME  | DEFAULT CURRENT_TIMESTAMP   | 登録日時                 |

**ユニーク制約**: `(guild_id, text)` の組み合わせで重複を防ぐ

```sql
CREATE TABLE IF NOT EXISTS hr_entries (
    id         INTEGER  PRIMARY KEY AUTOINCREMENT,
    guild_id   TEXT     NOT NULL,
    text       TEXT     NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(guild_id, text)
);
```

---

## ディレクトリ構成

```
hr-bot/
├── DESIGN.md               # 本ドキュメント
├── README.md               # セットアップ手順
├── fly.toml                # Fly.io デプロイ設定
├── Dockerfile              # コンテナ定義
├── requirements.txt        # Pythonパッケージ
├── .env.example            # 環境変数テンプレート
├── .gitignore
└── src/
    ├── main.py             # エントリーポイント
    ├── db.py               # DB接続・初期化
    └── cogs/
        └── hr.py           # HR関連コマンド（Cogクラス）
```

---

## 主要コンポーネント

### `src/main.py`
- Botのインスタンス化と起動
- Cogの読み込み
- 環境変数（Discordトークン）の読み込み

### `src/db.py`
- `aiosqlite` による非同期DB接続
- テーブルの初期化（`init_db()`）
- CRUD関数:
  - `add_hr(guild_id, text)` → 登録
  - `get_random_hr(guild_id)` → ランダム取得
  - `list_hr(guild_id)` → 一覧取得
  - `remove_hr(guild_id, entry_id)` → 削除

### `src/cogs/hr.py`
- `discord.py` の `Cog` クラスとして実装
- 各スラッシュコマンドの `app_commands.command` デコレータで定義

---

## 環境変数

| 変数名          | 説明                          |
|-----------------|-------------------------------|
| `DISCORD_TOKEN` | Discord Developer Portal で取得したBotトークン |
| `DB_PATH`       | SQLiteファイルのパス（例: `/data/hr.db`） |

---

## Fly.io デプロイ構成

### 永続ボリューム
- マウントパス: `/data`
- SQLiteファイル: `/data/hr.db`
- サイズ: 1GB（無料枠内）

### `fly.toml` の主要設定
```toml
[build]

[[mounts]]
  source      = "hr_data"
  destination = "/data"

[env]
  DB_PATH = "/data/hr.db"
```

### Dockerfile 方針
- `python:3.11-slim` ベースイメージ
- `requirements.txt` からパッケージインストール
- `CMD ["python", "src/main.py"]`

---

## Botの権限設定（Discord Developer Portal）

### Bot Permissions（整数値: `2048`）
- `Send Messages`

### Privileged Gateway Intents
- 不要（スラッシュコマンドのみのため）

### OAuth2 スコープ
- `bot`
- `applications.commands`

---

## 開発フロー

1. Discord Developer Portal でアプリケーション・Botを作成しトークンを取得
2. ローカルで `.env` を設定し動作確認
3. Fly.io アカウント作成 → `flyctl` CLI インストール
4. `fly launch` でアプリ作成、ボリューム作成
5. `fly secrets set DISCORD_TOKEN=xxx` でトークンを設定
6. `fly deploy` でデプロイ

---

## 将来の拡張案（実装対象外）

- `/hr` 投稿後に元メッセージを削除するオプション
- 区切り線にカテゴリタグをつける
- 管理者のみ削除可能にするオプション
