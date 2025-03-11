import json
from pathlib import Path


class BahamutDB:
    def __init__(self, anime2users_file_path: Path, user2animes_file_path: Path, bahamut_web_info_file_path: Path):
        # for path in [anime2users_file_path, user2animes_file_path, bahamut_web_info_file_path]:
        #     if not path.exists() or path.stat().st_size == 0:
        #         with path.open('w', encoding='utf-8') as f:
        #             json.dump({}, f, indent=4)
                    
        self.info_file_path = bahamut_web_info_file_path
    
    def save_infos(self, infos: dict[str, dict[str, str]]) -> None:
        """
        anime informations is from web_spider/bahamut_web_spider.py

        Args:
            infos data structure:
                dict["naruto", dict["viewers": "200", "episode": "5", ...]...]
        """
        with self.info_file_path.open('r+', encoding='utf-8') as f:
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
        with self.info_file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('infos', {})
    
    def save_schedule(self, schedule: dict[str, list[list[str]]]) -> None:
        with self.info_file_path.open('r+', encoding='utf-8') as f:
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
        with self.info_file_path.open('r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('schedule', "")
        