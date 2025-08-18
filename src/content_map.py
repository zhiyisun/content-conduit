import json
import os

class ContentMap:
    def __init__(self, config_path: str):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.map = json.load(f)

    def get_folder(self, logical_name: str) -> str:
        return self.map.get(logical_name)

    def all_mappings(self):
        return self.map.items()
