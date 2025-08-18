import json
import os

class ContentConfig:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)

    def get_folder(self, logical_name: str) -> str:
        item = self.config.get(logical_name)
        return item.get('folder') if item else None

    def get_prompt(self, logical_name: str) -> str:
        item = self.config.get(logical_name)
        return item.get('prompt') if item else None

    def all_items(self):
        return self.config.items()
