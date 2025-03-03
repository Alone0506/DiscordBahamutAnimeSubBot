import json
from pathlib import Path

INFO_FILE_PATH = Path(__file__).parent.parent / 'db/bahamut_web_info.json'

class BahamutDB:
    def __init__(self):
        try:
            with INFO_FILE_PATH.open('a+', encoding='utf-8') as f:
                f.seek(0)
                json.load(f)
        except:
            print("can't read the bahamut file")
            with INFO_FILE_PATH.open('w', encoding='utf-8') as f:
                json.dump({}, f, indent=4)
    
    def save_infos(self, infos: dict[str, dict[str, str]]) -> None:
        """
        anime informations is from web_spider/bahamut_web_spider.py

        Args:
            infos data structure:
                dict["naruto", dict["viewers": "200", "episode": "5", ...]...]
        """
        with INFO_FILE_PATH.open('r+', encoding='utf-8') as f:
            data = json.load(f)
            data['infos'] = dict((name, info) for name, info in infos.items())
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
                    
    def get_infos(self) -> dict[str, dict[str, str]]:
        """
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
        with INFO_FILE_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('infos', {})
    
    def save_schedule(self, schedule: dict[str, list[list[str]]]) -> None:
        with INFO_FILE_PATH.open('r+', encoding='utf-8') as f:
            data = json.load(f)
            data['schedule'] = schedule
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        
    def get_schedule(self) -> dict[str, list[list[str]]]:
        """
        Returns:
            dict[
                "星期一": [(name, time, url), ...], 
                "星期二": [(name, time, url), ...],
                ...
            ]
        """
        with INFO_FILE_PATH.open('r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('schedule', "")
        