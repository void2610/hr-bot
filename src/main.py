"""Botのエントリーポイント"""

import asyncio
import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from src import db

# .envファイルから環境変数を読み込む
load_dotenv()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# 読み込むCogのモジュールリスト
COGS = [
    "src.cogs.hr",
]


class HRBot(commands.Bot):
    def __init__(self) -> None:
        super().__init__(
            command_prefix="!",  # スラッシュコマンドのみ使用するが設定は必須
            intents=discord.Intents.default(),
        )

    async def setup_hook(self) -> None:
        """Bot起動前の初期化処理"""
        # DBを初期化
        await db.init_db()
        logger.info("データベースを初期化しました")

        # Cogを読み込み
        for cog in COGS:
            await self.load_extension(cog)
            logger.info("Cogを読み込みました: %s", cog)

        # スラッシュコマンドをDiscordに同期
        await self.tree.sync()
        logger.info("スラッシュコマンドを同期しました")

    async def on_ready(self) -> None:
        logger.info("Botが起動しました: %s (ID: %s)", self.user, self.user.id)


async def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("環境変数 DISCORD_TOKEN が設定されていません")

    bot = HRBot()
    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
