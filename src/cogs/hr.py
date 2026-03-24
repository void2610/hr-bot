"""HR（区切り線）コマンドのCog"""

import discord
from discord import app_commands
from discord.ext import commands

from src import db


class HR(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="hr", description="登録済みの区切り線をランダムに投稿します")
    async def hr(self, interaction: discord.Interaction) -> None:
        text = await db.get_random_hr(interaction.guild_id)
        if text is None:
            await interaction.response.send_message(
                "区切り線が登録されていません。`/addhr` で登録してください。",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(text)

    @app_commands.command(name="addhr", description="区切り線を登録します")
    @app_commands.describe(text="登録する区切り線の文字列（絵文字も使用可）")
    async def addhr(self, interaction: discord.Interaction, text: str) -> None:
        if len(text) > 2000:
            await interaction.response.send_message(
                "区切り線は2000文字以内で登録してください。",
                ephemeral=True,
            )
            return

        success = await db.add_hr(interaction.guild_id, text)
        if success:
            await interaction.response.send_message(f"✅ 区切り線を登録しました: {text}")
        else:
            await interaction.response.send_message(
                "その区切り線はすでに登録されています。",
                ephemeral=True,
            )

    @app_commands.command(name="listhr", description="登録済みの区切り線一覧を表示します")
    async def listhr(self, interaction: discord.Interaction) -> None:
        entries = await db.list_hr(interaction.guild_id)
        if not entries:
            await interaction.response.send_message(
                "区切り線が登録されていません。`/addhr` で登録してください。",
                ephemeral=True,
            )
            return

        # 一覧を番号付きで整形
        lines = [f"`{i + 1}.` (ID:{entry_id}) {text}" for i, (entry_id, text) in enumerate(entries)]
        body = "\n".join(lines)
        await interaction.response.send_message(
            f"**登録済み区切り線一覧（{len(entries)}件）**\n{body}",
            ephemeral=True,
        )

    @app_commands.command(name="removehr", description="区切り線を削除します")
    @app_commands.describe(entry_id="/listhr で表示されたIDを指定します")
    async def removehr(self, interaction: discord.Interaction, entry_id: int) -> None:
        deleted_text = await db.remove_hr(interaction.guild_id, entry_id)
        if deleted_text is None:
            await interaction.response.send_message(
                f"ID `{entry_id}` の区切り線は見つかりませんでした。`/listhr` でIDを確認してください。",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(f"🗑️ 区切り線を削除しました: {deleted_text}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(HR(bot))
