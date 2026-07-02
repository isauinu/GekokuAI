import sys
from datetime import datetime


is_verbose = False

def log(message):
    print(f"[{datetime.now()}] [Log] {message}", flush=True)

def info(message):
    print(f"[{datetime.now()}] [Info] {message}", flush=True)

def success(message):
    print(f"[{datetime.now()}] [SUCCESS] {message}", flush=True)

def warn(message):
    print(f"[{datetime.now()}] [Warn] {message}", flush=True)

def error(message):
    print(f"[{datetime.now()}] [Error] {message}", flush=True)

def fatal(message):
    print(f"[{datetime.now()}] [FATAL] {message}", flush=True)
    sys.exit(1)

def enable_verbose():
    global is_verbose
    is_verbose = True

def verbose(message):
    if is_verbose:
        print(f"[{datetime.now()}] [Verbose] {message}", flush=True)