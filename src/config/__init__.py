"""Config module"""

from pathlib import Path

CONFIG_DIR = Path(__file__).parent

def get_config_path(name: str) -> str:
    """Get path to config file."""
    return str(CONFIG_DIR / name)
