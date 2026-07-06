import os
from pathlib import Path
try:
    import tomlib
except ImportError:
    import tomli as tomlib
from utils.toml_manager import *
from utils.logger import *
from utils.runtime import Runtime
from utils.downloader import DownloadMetadata

HOME = os.getenv('HOME') or os.path.expanduser('~')
GEKOKU_HOME = Path(HOME, ".gekokuai")

GEKOKU_PROJECT_ROOT = Path(__file__).resolve().parent.parent

CONFIG_PATH = Path(GEKOKU_HOME, "config", "config.toml")
try:
    CONFIG_DATA = read_toml(CONFIG_PATH)
except Exception as e:
    error("Cannot read configuration data")
    CONFIG_DATA = {
        "metadata": {
            "CPU_BACKEND": "",
            "GPU_BACKEND": "GPU"
        },
        "server": {
            "host": "127.0.0.1",
            "port": 8080
        },
        "location": {
            "workspace": f"{Path(Path.home(), ".gekokuai")}",
            "models_path": f"{Path(Path.home(), ".gekokuai", "models")}",
            "venv_path": f"{Path(Path.home(), ".gekokuai", "venv")}",
            "log_path": f"{Path(Path.home(), ".gekokuai", "logs")}",
            "tmp_path": f"{Path(Path.home(), ".gekokuai", "tmp")}",
        },
        "llama_cpp": {
            "llama_cpp_path": f"{Path(Path.home(), ".gekokuai" "llama.cpp")}",
        },
        "security": {
            "host_managed_endpoints": True,
            "allowed_hosts": ["127.0.0.1", "::1"]
        }
    }


MODELS_DIR_PATH = Path(f"{GEKOKU_HOME}", "models")

RUNTIME_DIR_PATH = Path(f"{GEKOKU_HOME}", "runtime")
RUNTIME_SNAPSHOT_FILE_PATH = Path(f"{GEKOKU_HOME}", "runtime", "runtime.toml")
if not RUNTIME_DIR_PATH.is_dir():
    warn("Runtime folder to store server information doesn't exist")

class RuntimeSnapshot:
        def __getitem__(self, key):
            try:
                data = read_toml(RUNTIME_SNAPSHOT_FILE_PATH)
            except Exception as e:
                error("Runtime snapshot cannot be loaded!")
                data = {
                "server": {
                    "running": False,
                    "pid": 0,
                    "models": [],
                    "host": "",
                    "port": "",
                    "log_file": ""
                    }
                }
            return data[key]
RUNTIME_SNAPSHOT = RuntimeSnapshot()

parent_folder = Path(__file__).resolve().parent.parent.parent
GEKOKUAI_METADATA_PATH = Path(f"{parent_folder}", "metadata.toml")
if not GEKOKUAI_METADATA_PATH.is_file():
    error("No metadata file is detected on the expected path")
    GEKOKUAI_METADATA_DATA = {
        "metadata": {
            "version": "Unknown",
            "release_date": "Unknown",
            "license": "MIT",
        }
    }
else:
    GEKOKUAI_METADATA_DATA = read_toml(GEKOKUAI_METADATA_PATH)

GEKOKUAI_VERSION = GEKOKUAI_METADATA_DATA["metadata"]["version"]
GEKOKUAI_BUILD_RELEASE_DATE = GEKOKUAI_METADATA_DATA["metadata"]["release_date"]
GEKOKUAI_LICENSE = GEKOKUAI_METADATA_DATA["metadata"]["license"]

LOG_DIR_PATH = Path(f"{GEKOKU_HOME}", "logs")

API_PREFIX = "/api/v1"

RUNTIME = Runtime()

DOWNLOAD = DownloadMetadata()

VENV_PYTHON = f"{CONFIG_DATA["location"]["venv_path"]}/bin/python"