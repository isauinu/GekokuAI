import os
from pathlib import Path
try:
    import tomlib
except ImportError:
    import tomli as tomlib
from utils.toml_manager import *

HOME = os.getenv('HOME') or os.path.expanduser('~')

CONFIG_PATH = Path(HOME, ".gekokuai", "config", "config.toml")
CONFIG_DATA = read_toml(CONFIG_PATH)

GEKOKU_HOME = CONFIG_DATA["location"]["workspace"]
MODELS_DIR_PATH = Path(f"{GEKOKU_HOME}", "models")
RUNTIME_DIR_PATH = Path(f"{GEKOKU_HOME}", "runtime")

parent_folder = Path(__file__).resolve().parent.parent.parent
GEKOKUAI_METADATA_PATH = Path(f"{parent_folder}", "metadata.toml")
GEKOKUAI_METADATA_DATA = read_toml(GEKOKUAI_METADATA_PATH)
GEKOKUAI_VERSION = GEKOKUAI_METADATA_DATA["metadata"]["version"]