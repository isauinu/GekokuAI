from utils.logger import *
from pathlib import Path
from utils.globals import MODELS_DIR_PATH
from utils.toml_manager import *
from utils.exception_handling import *
from pathlib import Path
import re
from utils.file_size_formatter import *
from huggingface_hub import scan_cache_dir

def remove_model(args):
    if check_model_exists(args.remove_model):
        model_info_path = Path(f"{MODELS_DIR_PATH}", f"{args.remove_model}.toml")
        model_info = read_toml(model_info_path)
        model_file_path = model_info["metadata"]["path"]
        if not Path(model_file_path).is_file():
            error("Unable to locate the file of the model reference in the info file")
            fatal("Aborting...")
        verbose(f"Model file path: {model_file_path}")
        model_folder_path = Path(model_file_path).parent
        quant_pattern = re.compile(r"\b(I?Q\d_\w+|BF16|F16|F32|MXFP4\w*)\b", re.IGNORECASE)
        model_id = model_info["id"]
        scheduled_deleted_files = []
        for f in model_folder_path.iterdir():
            match = quant_pattern.search(f.name)
            if not match:
                continue
            quant_type = match.group(1).upper()
            verbose(f"{f.name}: {quant_type}")
            if quant_type in model_id:
                scheduled_deleted_files.append(f.name)
        
        if Path(model_info["metadata"]["mmproj_path"]).is_file() and not Path(model_info["metadata"]["mmproj_path"]).name in scheduled_deleted_files:
            scheduled_deleted_files.append(Path(model_info["metadata"]["mmproj_path"]).name)
        verbose(f"List of associated files based on quantization: {scheduled_deleted_files}")

        verbose(f"model's commit hash: {model_info["metadata"]["commit_hash"]}")
        cache = scan_cache_dir()
        strategy = cache.delete_revisions(model_info["metadata"]["commit_hash"])
        verbose(f"Deletion strategy: {strategy}")

        max_file_width = max(len(item) for item in scheduled_deleted_files) + 5 or len("Total space freed")
        max_file_size_width = 10
        total_deletion_size = 0
        print(f"The following files associated with {args.remove_model} will be deleted:\n")
        print(f"{"File name":<{max_file_width}}{"Size":<{max_file_width}}")
        print(f"{"":-^{max_file_width + max_file_size_width}}")
        for f in scheduled_deleted_files:
            file_path = Path(model_folder_path, f)
            file_size = file_path.stat().st_size
            print(f"{f:<{max_file_width}}{format_size(file_size):<{max_file_size_width}}")
            total_deletion_size += file_size
        print(f"\n{"Total space freed":<{max_file_width}}{format_size(total_deletion_size):<{max_file_size_width}}")
        while True:
            try:
                proceed_choice_input = input(f"Proceed deletion for the following files? (y/[N]): ")
                proceed_choice = "n" if proceed_choice_input == "" else str(proceed_choice_input)
                break
            except ValueError:
                sys.stdout.write("\033[A\033[K")
                sys.stdout.flush()
        
        if proceed_choice in ["y", "Y", "yes", "Yes", "YES"]:
            pass
        else:
            print("Removal cancelled...")
            return
        
        strategy.execute()
        model_info_path.unlink(missing_ok=True)

        print("\nModel has successfully been deleted.")
        return

        choice = input(f"Do you really want to remove {args.remove_model} model? (y/n): ")
        if choice in ['y', 'Y', 'yes', 'Yes', 'YES']:
            log(f"Removing {args.remove_model} from shelf...")
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