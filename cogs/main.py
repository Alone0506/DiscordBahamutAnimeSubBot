import logging

import discord
from discord.ext import commands

logger = logging.getLogger('discord')

class Main(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # 當機器人完成啟動時
    @commands.Cog.listener()
    async def on_ready(self):
        slash = await self.bot.tree.sync()
        print(f"載入 {len(slash)} 個斜線指令")
        logger.info(f'{self.bot.user} 已登入')
        game = discord.Game('Mumei')
        # 變更bot狀態, status: online, offline, idle, dnd, invisible
        await self.bot.change_presence(status=discord.Status.online, activity=game)
        print(f"cog loading finish, {self.bot.user} 已登入")

# Cog 載入 Bot 中
async def setup(bot: commands.Bot):
    await bot.add_cog(Main(bot))
