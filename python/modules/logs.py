from utils.globals import RUNTIME_SNAPSHOT
from utils.logger import *
import subprocess
from utils.interrupt_handler import *

def tail_logs():
    if RUNTIME_SNAPSHOT["server"]["log_file"]:
        subprocess.run(["tail", "-n", "100", "-f", RUNTIME_SNAPSHOT["server"]["log_file"]])
    else:
        error("daemon is not online")