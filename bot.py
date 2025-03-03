import asyncio
import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
import shutil
import discord
from discord.ext import commands


BOT_AUTHOR_ID = int(os.getenv("BOT_AUTHOR_ID", "0"))
DC_TOKEN = os.getenv("DC_TOKEN", "")

########################### setting log ###########################
folder_path = Path(__file__).parent / "log" / "bot"
if folder_path.exists():
    shutil.rmtree(folder_path)
folder_path.mkdir()

handler = TimedRotatingFileHandler(filename=folder_path / "bot.log", when='midnight', interval=1, backupCount=14, encoding='utf-8')
handler.suffix = "%Y-%m-%d_%H-%M-%S.log"
handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)-8s] %(name)s: %(message)s', "%Y-%m-%d %H:%M:%S"))

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)
###################################################################

bot = commands.Bot(command_prefix = '$', intents = discord.Intents.all())

def check_guild(ctx: commands.Context):
    return ctx.author.id == BOT_AUTHOR_ID

# 載入指令程式檔案
@bot.command()
@commands.check(check_guild)
async def load(ctx: commands.Context, extension):
    await bot.load_extension(f"cogs.{extension}")
    await ctx.send(f"Loaded {extension} done.")

# 卸載指令檔案
@bot.command()
@commands.check(check_guild)
async def unload(ctx: commands.Context, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send(f"UnLoaded {extension} done.")

# 重新載入程式檔案
@bot.command()
@commands.check(check_guild)
async def reload(ctx: commands.Context, extension):
    await bot.reload_extension(f"cogs.{extension}")
    await ctx.send(f"ReLoaded {extension} done.")

async def main():
    async with bot:
        await bot.load_extension(f"cogs.main")
        await bot.load_extension(f"cogs.bahamut")
        await bot.start(DC_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
