import os
from pathlib import Path
try:
    import tomlib
except ImportError:
    import tomli as tomlib
from utils.toml_manager import *
from utils.logger import *

HOME = os.getenv('HOME') or os.path.expanduser('~')

CONFIG_PATH = Path(HOME, ".gekokuai", "config", "config.toml")
CONFIG_DATA = read_toml(CONFIG_PATH)

GEKOKU_HOME = CONFIG_DATA["location"]["workspace"]

MODELS_DIR_PATH = Path(f"{GEKOKU_HOME}", "models")

RUNTIME_DIR_PATH = Path(f"{GEKOKU_HOME}", "runtime")
RUNTIME_DAEMON_FILE_PATH = Path(f"{GEKOKU_HOME}", "runtime", "runtime.toml")
RUNTIME_DAEMON_DATA = read_toml(RUNTIME_DAEMON_FILE_PATH)

parent_folder = Path(__file__).resolve().parent.parent.parent
GEKOKUAI_METADATA_PATH = Path(f"{parent_folder}", "metadata.toml")
if not GEKOKUAI_METADATA_PATH.is_file():
    error("No metadata file is detected on the expected path")
    GEKOKUAI_METADATA_DATA = {
        "metadata": {
            "version": "Unknown"
        }
    }
else:
    GEKOKUAI_METADATA_DATA = read_toml(GEKOKUAI_METADATA_PATH)

GEKOKUAI_VERSION = GEKOKUAI_METADATA_DATA["metadata"]["version"]