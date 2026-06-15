from utils.vars import MODELS_DIR_PATH
from utils.logger import *

#Added abstraction layer
def check_model_exists(model):
    model_id = None
    for file in MODELS_DIR_PATH.iterdir():
        if f"{model}.toml" == file.name:
            log(f"Found model: {file.stem}")
            model_id = file
    if model_id:
        return True
    else:
        return False