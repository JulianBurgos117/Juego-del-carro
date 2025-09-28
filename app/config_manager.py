# app/config_manager.py
import json
import os

class ConfigManager:
    """
    Helper to load and save game configuration and obstacle list in a JSON file.
    """

    def __init__(self, path="json/config.json"):
        self.path = path
        self.data = {"config": {}, "obstacles": []}
        self._load_if_exists()

    def _load_if_exists(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.data = loaded
            except Exception:
                # keep defaults on error
                self.data = {"config": {}, "obstacles": []}

    def get_config(self):
        return self.data.get("config", {})

    def get_obstacles(self):
        return self.data.get("obstacles", [])

    def add_obstacle(self, obs):
        self.data.setdefault("obstacles", []).append(obs)
        self._save()

    def remove_obstacle_by_index(self, idx):
        obs = self.data.get("obstacles", [])
        if 0 <= idx < len(obs):
            removed = obs.pop(idx)
            self._save()
            return removed
        return None

    def _save(self):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w") as f:
            json.dump(self.data, f, indent=4)

    def save_file(self, path):
        with open(path, "w") as f:
            json.dump(self.data, f, indent=4)