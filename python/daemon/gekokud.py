from pathlib import Path
import sys
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import signal
import os
from utils.toml_manager import *
from utils.globals import CONFIG_DATA, RUNTIME
from utils.logger import *
from utils.daemon_cleanup import *
from daemon.api.app import app
import uvicorn

signal.signal(signal.SIGTERM, daemon_cleanup)
signal.signal(signal.SIGINT, daemon_cleanup)

RUNTIME.running = True
RUNTIME.pid = os.getpid()
RUNTIME.host = os.getenv("GEKOKU_HOST")
RUNTIME.port = int(os.getenv("GEKOKU_PORT"))
RUNTIME.log_file = os.getenv("GEKOKU_LOG_FILE")

host = CONFIG_DATA["server"]["host"]
port = CONFIG_DATA["server"]["port"]
uvicorn.run(app, host=host, port=port)