import sys
from datetime import datetime

def log(message):
    print(f"[{datetime.now()}] [Log] {message}")

def info(message):
    print(f"[{datetime.now()}] [Info] {message}")

def success(message):
    print(f"[{datetime.now()}] [SUCCESS] {message}")

def warn(message):
    print(f"[{datetime.now()}] [Warn] {message}")

def error(message):
    print(f"[{datetime.now()}] [Error] {message}")

def fatal(message):
    print(f"[{datetime.now()}] [FATAL] {message}")
    sys.exit(1)