"""データベース接続・初期化およびCRUD関数"""

import os
import aiosqlite

# 環境変数からDBパスを取得（未設定時はカレントディレクトリのhr.db）
DB_PATH = os.getenv("DB_PATH", "./hr.db")


async def init_db() -> None:
    """テーブルを初期化する"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS hr_entries (
                id         INTEGER  PRIMARY KEY AUTOINCREMENT,
                guild_id   TEXT     NOT NULL,
                text       TEXT     NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(guild_id, text)
            )
        """)
        await db.commit()


async def add_hr(guild_id: int, text: str) -> bool:
    """区切り線を登録する。重複時はFalseを返す。"""
    async with aiosqlite.connect(DB_PATH) as db:
        try:
            await db.execute(
                "INSERT INTO hr_entries (guild_id, text) VALUES (?, ?)",
                (str(guild_id), text),
            )
            await db.commit()
            return True
        except aiosqlite.IntegrityError:
            # UNIQUE制約違反（重複登録）
            return False


async def get_random_hr(guild_id: int) -> str | None:
    """サーバーの区切り線リストからランダムに1件取得する。未登録時はNoneを返す。"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT text FROM hr_entries WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1",
            (str(guild_id),),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def get_hr_by_index(guild_id: int, index: int) -> str | None:
    """登録順のインデックス（1始まり）で区切り線を取得する。範囲外の場合はNoneを返す。"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT text FROM hr_entries WHERE guild_id = ? ORDER BY created_at ASC LIMIT 1 OFFSET ?",
            (str(guild_id), index - 1),
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None


async def list_hr(guild_id: int) -> list[tuple[int, str]]:
    """サーバーの区切り線リストをID付きで全件取得する。"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, text FROM hr_entries WHERE guild_id = ? ORDER BY created_at ASC",
            (str(guild_id),),
        ) as cursor:
            return await cursor.fetchall()


async def remove_hr(guild_id: int, entry_id: int) -> str | None:
    """指定IDの区切り線を削除する。存在しない場合はNoneを返す。"""
    async with aiosqlite.connect(DB_PATH) as db:
        # 削除前にテキストを取得（削除確認メッセージ用）
        async with db.execute(
            "SELECT text FROM hr_entries WHERE id = ? AND guild_id = ?",
            (entry_id, str(guild_id)),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            return None

        await db.execute(
            "DELETE FROM hr_entries WHERE id = ? AND guild_id = ?",
            (entry_id, str(guild_id)),
        )
        await db.commit()
        return row[0]
