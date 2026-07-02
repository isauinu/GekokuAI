from utils.logger import *
from pathlib import Path
from utils.globals import MODELS_DIR_PATH
from utils.toml_manager import *
from utils.exception_handling import *

def remove_model(args):
    if check_model_exists(args.remove_model):
        choice = input(f"Do you really want to remove {args.remove_model} model? (y/n): ")
        if choice in ['y', 'Y', 'yes', 'Yes', 'YES']:
            log(f"Removing {args.remove_model} from shelf...")
            model_info_path = Path(f"{MODELS_DIR_PATH}", f"{args.remove_model}.toml")
            model_info = read_toml(model_info_path)
            model_file_path = Path(model_info["metadata"]["path"])
            mmproj_file_path = Path(model_info["metadata"]["mmproj_path"])
            log(f"Removing model file, Path: {model_file_path}")
            model_file_path.unlink(missing_ok=True)
            if mmproj_file_path.name:
                log(f"Removing mmproj file, Path: {mmproj_file_path}")
                mmproj_file_path.unlink(missing_ok=True)
            log("Deleting model information...")
            model_info_path.unlink(missing_ok=True)
            success("Model has successfully been removed")
        else:
            info("Removal cancelled...")
    else:
        error("No model found associated with that name")