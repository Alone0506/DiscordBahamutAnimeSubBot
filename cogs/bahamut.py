import logging
from pathlib import Path
import datetime
import json

import discord
from discord import app_commands
from discord.ext import commands, tasks

from cogs.bahamut_web_spider import BahamutAPI
from cogs.bahamut_web_info_handler import BahamutDB

ANIME2USERS_FILE_PATH = Path(__file__).parent.parent / 'db' / 'anime2users.json'
USER2ANIMES_FILE_PATH = Path(__file__).parent.parent / 'db' / 'user2animes.json'
BAHAMUT_WEB_INFO_FILE_PATH = Path(__file__).parent.parent / 'db' / 'bahamut_web_info.json'
TEST_MODE = False
logger = logging.getLogger('discord')

class Channel_Embed(discord.Embed):
    def __init__(self, info: dict[str, str]):
        name = info['name']
        viewers = info['viewers']
        episode = "此為OVA或電影" if info['episode'] is None else info['episode']
        url = info['url']
        thumbnail_url = info['thumbnail_url']
        update_time = info['update_time']
        
        super().__init__(color=0x0385B1, title=name, url=url)  # 0x0385B1 = Bahamut 品牌顏色
        self.add_field(name="觀看次數", value=viewers, inline=True)
        self.add_field(name="最新集數", value=episode, inline=True)
        self.add_field(name="最新更新時間", value=update_time, inline=True)
        self.set_thumbnail(url=thumbnail_url)

class Bahamut(commands.Cog):
    time = []
    """
    The ratelimit for editing a channel is 2 requests per 10 minutes per channel.
    So, if not in TEST_MODE, the time interval must be greater then 5 min.
    https://support.discord.com/hc/en-us/community/posts/360067755532-Increase-rate-limit-for-editing-channel-description
    """
    if TEST_MODE:
        time = [datetime.time(hour=i, minute=j, second=k) for i in range(24) for j in range(60) for k in range(0, 60, 30)]
    else:
        time = [datetime.time(hour=i, minute=j) for i in range(24) for j in range(0, 60, 10)]
    
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bahamut_db = BahamutDB()
        self.bahamut_api = BahamutAPI(TEST_MODE)
        self.update_db.start()
        
    def cog_unload(self):
        self.update_db.cancel()
        
    @app_commands.command(name = "anime_help", description = "查看指令功能與使用方式")
    async def anime_help(self, interaction: discord.Interaction):
        help_str = (
            "## 🎥 動漫指令使用說明\n"
            "歡迎使用動漫通知機器人！以下是可用指令：\n\n"
            "**📜 動漫資訊查詢**\n"
            "🔹 `/anime_list` - 查看目前更新中的所有動漫\n"
            "🔹 `/anime_sub_list` - 查看你訂閱的動漫清單\n\n"
            "**📌 訂閱與取消訂閱**\n"
            "🔹 `/anime operation:Subscribe anime_name:<動漫名稱>` - 訂閱指定動漫\n"
            "🔹 `/anime operation:Unsubscribe anime_name:<動漫名稱>` - 取消訂閱指定動漫\n"
            "🔹 `/anime_unsub_all` - 取消訂閱所有動漫\n\n"
            "**📢 動漫更新提醒**\n"
            "當你訂閱的動漫有新集數時，機器人會私訊通知你 📩！\n\n"
            "📌 **資料來源**: [巴哈姆特動畫瘋](https://ani.gamer.com.tw/)\n"
        )
        await interaction.response.send_message(help_str)
        
    @app_commands.command(name = "anime_list", description = "View all currently updating anime")
    async def anime_list(self, interaction: discord.Interaction):
        anime_infos = self.bahamut_db.get_infos()
        send_embeds = [Channel_Embed(anime_info) for _, anime_info in anime_infos.items()]
        
        if len(send_embeds) > 0:
            await interaction.response.send_message(embeds=send_embeds[:10])
        for i in range(10, len(send_embeds), 10):
            await interaction.followup.send(embeds=send_embeds[i:i+10])

    @app_commands.command(name = "anime_sub_list", description = "View your subscribed anime list.")
    async def anime_sub_list(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        with USER2ANIMES_FILE_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
            sub_animes_name = set(data.get(user_id, []))
            
        with BAHAMUT_WEB_INFO_FILE_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
            new_animes_name = set(data.get('infos', {}).keys())
            
        res = ""
        for sub_anime_name in sub_animes_name:
            if sub_anime_name in new_animes_name:
                res += f"\n- {sub_anime_name}"
            else:
                res += f"\n- ~~{sub_anime_name}~~  (非新番)"
        if res == "":
            res = "尚未訂閱任何動漫"
        else:
            res = "### 📌 訂閱的動漫清單 📌" + res

        await interaction.response.send_message(res)
        
    @app_commands.command(name = "anime_unsub_all", description = "Unsubscribe all anime")
    async def anime_unsub_all(self, interaction: discord.Interaction):
        user_id = str(interaction.user.id)
            
        with USER2ANIMES_FILE_PATH.open('r+', encoding='utf-8') as f:
            # read the file
            data = json.load(f)
            anime_names = set(data.get(user_id, []))
            del data[user_id]
            
            # write the file
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            
        with ANIME2USERS_FILE_PATH.open('r+', encoding='utf-8') as f:
            # read the file
            data = json.load(f)
            for anime_name in anime_names:
                users = set(data.get(anime_name, []))
                users.discard(user_id)
                data[anime_name] = list(users)
                if len(users) == 0: # if no user subscribe this anime, delete this anime
                    del data[anime_name]
            
            # write the file
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)

        user_name = interaction.user.name
        await interaction.response.send_message(f"{user_name} unsubscribe all done.")


    @app_commands.command(name = "anime", description = "What anime want to subscribe / unsubscribe")
    @app_commands.choices(
        operation = [
            app_commands.Choice(name = "Subscribe", value = "sub"),
            app_commands.Choice(name = "Unsubscribe", value = "unsub"),
        ]
    )
    async def anime(self, interaction: discord.Interaction, operation: app_commands.Choice[str], anime_name: str):
        user_id = str(interaction.user.id)
        anime_name = anime_name.strip()
        
        with ANIME2USERS_FILE_PATH.open('r+', encoding='utf-8') as f:
            # read the file
            data = json.load(f)
            users = set(data.get(anime_name, []))
            if operation.value == "sub":
                users.add(user_id)
            elif operation.value == "unsub":
                users.discard(user_id)
            data[anime_name] = list(users)
            if len(users) == 0:
                del data[anime_name]
            
            # write the file
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)
            
        with USER2ANIMES_FILE_PATH.open('r+', encoding='utf-8') as f:
            # read the file
            data = json.load(f)
            animes_names = set(data.get(user_id, []))
            if operation.value == "sub":
                animes_names.add(anime_name)
            elif operation.value == "unsub":
                animes_names.discard(anime_name)
            data[user_id] = list(animes_names)
            if len(animes_names) == 0:
                del data[user_id]
            
            # write the file
            f.seek(0)
            f.truncate()
            json.dump(data, f, indent=4)

        user_name = interaction.user.name
        await interaction.response.send_message(f"{user_name} {operation.value}scribe {anime_name} done.")

    @tasks.loop(time=time)
    async def update_db(self):
        old_infos = self.bahamut_db.get_infos()
        res = self.bahamut_api.run_spider()
        if res is False:
            logger.warning('get anime information from Bahamut failed, skip update bahamut channel...')
        new_infos = self.bahamut_api.get_newest_anime_infos()
        
        # compare old_infos and new_infos to know which anime is updated
        update_animes: dict[str, dict[str, str]] = {}
        for anime_name, anime_infos in old_infos.items():
            if anime_name in new_infos and anime_infos["update_time"] != new_infos[anime_name]["update_time"]:
                update_animes[anime_name] = new_infos[anime_name]
        
        dm = self.create_dm(update_animes)
        await self.send_dm(dm)
                
        self.bahamut_db.save_infos(new_infos)
        self.bahamut_db.save_schedule(self.bahamut_api.get_newest_anime_schedule())
        
    def create_dm(self, update_animes: dict[str, dict[str, str]]) -> dict[str, list[Channel_Embed]]:
        dm: dict[str, list[Channel_Embed]] = {}  # key: user_id, value: [anime_info_embed, ...]
        with ANIME2USERS_FILE_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
            for name, infos in update_animes.items():
                if name not in data:
                    continue
                for user_id in data[name]:
                    if user_id not in dm:
                        dm[user_id] = []
                    dm[user_id].append(Channel_Embed(infos))
        return dm
        
    async def send_dm(self, dm: dict[str, list[Channel_Embed]]) -> None:
        for user_id, embeds in dm.items():
            user = self.bot.get_user(int(user_id))
            if user is None:
                continue
            if len(embeds) == 0:
                continue
            for i in range(0, len(embeds), 10):
                content = "## (ﾉ◕ヮ◕)ﾉ:･ﾟ✧  動漫更新 動漫更新  (ﾉ◕ヮ◕)ﾉ:･ﾟ✧\n" if i == 0 else None
                if i == 0:
                    await user.send(content=content, embeds=embeds[i:i+10])
    
    @update_db.before_loop
    async def wait_bot_ready(self):
        await self.bot.wait_until_ready()


async def setup(bot: commands.Bot):
    await bot.add_cog(Bahamut(bot))