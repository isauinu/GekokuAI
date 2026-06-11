from utils.vars import MODELS_DIR_PATH
from utils.logger import *
from pathlib import Path

#Added abstraction layer
def check_model_exists(model):
    model_id = None
    for file in MODELS_DIR_PATH.iterdir():
        if model in file.name:
            log(f"Found model: {file.stem}")
            model_id = file
    if model_id:
        return True
    else:
        return False
    
def check_dir_exists(dir):
    if dir.is_dir():
        return True
    else:
        return False
    
def check_file_exists(file):
    if file.is_file():
        return True
    else:
        return False