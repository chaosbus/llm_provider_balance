import json
import os
from pathlib import Path

CONFIG_DIR = Path(os.environ.get("APPDATA", Path.home() / ".config")) / "LLMProviderMon"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "api_keys": {
        "kimi": "",
        "deepseek": "",
        "siliconflow": "",
    },
    "refresh_interval": 60,
    "auto_refresh": True,
}


def load_config() -> dict:
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
        merged = dict(DEFAULT_CONFIG)
        merged.update(data)
        api_keys = dict(merged["api_keys"])
        api_keys.update(data.get("api_keys", {}))
        merged["api_keys"] = api_keys
        return merged
    return dict(DEFAULT_CONFIG)


def save_config(config: dict):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8"
    )
