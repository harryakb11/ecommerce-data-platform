import os
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config():
    environment = os.getenv("ENVIRONMENT", "dev")

    config_file = CONFIG_DIR / f"{environment}.yaml"

    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_file, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config
