from utils.vars import RUNTIME_DAEMON_DATA
from utils.logger import *
import subprocess
from utils.interrupt_handler import *

def tail_logs():
    if RUNTIME_DAEMON_DATA["server"]["log_file"]:
        subprocess.run(["tail", "-n", "100", "-f", RUNTIME_DAEMON_DATA["server"]["log_file"]])
    else:
        error("daemon is not online")