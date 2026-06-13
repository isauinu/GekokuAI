from utils.toml_manager import *
from utils.vars import RUNTIME_DAEMON_FILE_PATH
from utils.logger import *

def llama_cleanup(model):
    model_data = read_toml(RUNTIME_DAEMON_FILE_PATH)
    if model in model_data:
        del model_data[model]
        models_list = model_data["server"]["models"]
        models_list.remove(model)
        write_toml(RUNTIME_DAEMON_FILE_PATH, model_data)
        success(f"Successfully unloaded model {model}")
    else:
        error(f"No model found on runtime with the name {model}")