import json
from pathlib import Path
import requests

from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
FAKE_FILE_PATH = Path(__file__).parent.parent / 'db' / 'bahamut_fake_web_info.json'

class BahamutAPI:
    def __init__(self, is_test_mode: bool = False):
        self.url = "https://ani.gamer.com.tw/"
        self.is_test_mode = is_test_mode
        
    def run_spider(self) -> tuple[bool, dict[str, dict[str, str]], dict[str, list[list[str]]]]:
        """
        Runs the spider to fetch the latest anime information and schedule.
        Returns:
            tuple[bool, dict[str, dict[str, str]], dict[str, list[list[str]]]]: 
                A tuple containing:
                - A boolean indicating the success of the operation.
                - A dictionary with the latest anime information.
                - A dictionary with the latest anime schedule.
        """
        if self.is_test_mode:
            return True
        
        request = requests.get(self.url, headers=headers)
        if request.status_code != 200:
            print(f"抓動畫瘋出現error! status code: {request.status_code}")
            return False, {}, {}
        web_info = BeautifulSoup(request.text, 'html.parser')
        newest_anime_infos = self.__get_newest_anime_infos(web_info)
        newest_anime_schedule = self.__get_newest_anime_schedule(web_info)
        return True, newest_anime_infos, newest_anime_schedule
    
    def __get_newest_anime_infos(self, web_info: BeautifulSoup) -> dict[str, dict[str, str]]:
        """
        get Bahamut's anime infomations.

        Returns:
            data structure:
                {"naruto", {"name": "naruto",
                            "viewers": "200",
                            "episode": "5",
                            "url": "https://...",
                            "thumbnail_url": "https://...",
                            "update_time": "05/08 23:30"]
                            }
                ...
                }
        """
        anime_infos = {}
        
        if self.is_test_mode:
            with FAKE_FILE_PATH.open('r', encoding='utf-8') as f:
                data = json.load(f)
                anime_infos = data.get('infos', {})
            return anime_infos
        
        animes = web_info.select('.timeline-ver > .newanime-block > .newanime-date-area:not(.premium-block)')
        for anime in animes:
            anime_info = dict()
            # 動畫名稱
            name = anime.select_one('.anime-name-block > p').text.strip()
            anime_info['name'] = name
            # 觀看次數
            viewers = anime.select_one('.anime-watch-number > p').text.strip()
            anime_info['viewers'] = viewers
            # 最新集數
            episode = anime.select_one('.anime-episode').text.strip()
            anime_info['episode'] = episode
            # 動畫網址
            url = anime.select_one('a.anime-card-block').get('href')
            url = 'https://ani.gamer.com.tw/' + url
            anime_info['url'] = url
            # 動畫縮圖
            thumbnail_url = anime.select_one('img.lazyload').get('data-src')
            anime_info['thumbnail_url'] = thumbnail_url
            # 更新時間
            update_hour = anime.select_one('.anime-hours').text.strip()
            update_day = anime.select_one('.anime-date-info').contents[-1].string.strip()
            if update_day == "其他":
                anime_info['update_time'] = "其他"
            else:
                anime_info['update_time'] = f"{update_day} {update_hour}"

            anime_infos[name] = anime_info
        return anime_infos
    
    def __get_newest_anime_schedule(self, web_info: BeautifulSoup) -> dict[str, list[list[str]]]:
        """get bahamut weekly update schedule then return schedule's info.

        Returns:
            dict[
                "星期一": [(name, time, url), ...], 
                "星期二": [(name, time, url), ...],
                ...
            ]
        """
        anime_schedule: dict[str, list[list[str]]] = dict()
        
        if self.is_test_mode:
            with FAKE_FILE_PATH.open('r', encoding='utf-8') as f:
                data = json.load(f)
                anime_infos = data.get('schedule', {})
            return anime_infos
        
        days = web_info.select('.day-list')
        for day in days:
            # 取得禮拜幾的標題
            day_title = day.select_one('.day-title').text.strip()
            anime_schedule[day_title] = []

            # 取得動漫資訊
            anime_list = day.select('a.text-anime-info')
            for anime in anime_list:
                anime_time = anime.select_one('span.text-anime-time').text.strip()
                anime_name = anime.select_one('p.text-anime-name').text.strip()
                anime_url = 'https://ani.gamer.com.tw/' + anime.get('href')
                anime_schedule[day_title].append([anime_time, anime_name, anime_url])
        return anime_schedule
