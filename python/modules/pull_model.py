import os
os.environ["HF_HUB_VERBOSITY"] = "error"
os.environ["HF_HUB_DISABLE_XET"] = "1"

from huggingface_hub import HfApi, hf_hub_download, utils, get_hf_file_metadata, hf_hub_url, __version__
from huggingface_hub.errors import HfHubHTTPError
from pathlib import Path
from utils.logger import *
from utils.toml_manager import *
from utils.globals import MODELS_DIR_PATH, DOWNLOAD
import time
from utils.interrupt_handler import *
import re
from tqdm.auto import tqdm
from alive_progress import alive_bar
from utils.file_size_formatter import *
import shutil
import requests
from urllib3.exceptions import ProtocolError


class ProgressPipe(tqdm):
    def __init__(self, *args, **kwargs):
        self.manager = None
        self.bar = None
        super().__init__(*args, **kwargs)

        max_length = 35

        filename = (DOWNLOAD.current_filename[:max_length] + "...") if len(DOWNLOAD.current_filename) > max_length else DOWNLOAD.current_filename
        
        total_formatted = format_size(self.total) if self.total else "Unknown"

        title=f"File {DOWNLOAD.current_file}/{DOWNLOAD.total_files} | {filename} ({total_formatted})"

        terminal_width = shutil.get_terminal_size().columns
        stats_max_width = len("[999.99 GB/999.99 GB] ETA: 99:99:99 (999.99 MB/s)")
        padding = 10
        bar_length = max(10, terminal_width - len(title) - stats_max_width - padding)
        

        self.manager = alive_bar(self.total or 1, 
            manual=True, 
            monitor=False, 
            stats=False,
            length=bar_length,
            title=title
        )
        self.bar = self.manager.__enter__()

    def refresh(self, *args, **kwargs):
        super().refresh(*args, **kwargs)
        if not self.bar:
            return
        if self.total:
            DOWNLOAD.downloaded_size = self.n
            DOWNLOAD.downloaded_size = (
                DOWNLOAD.completed_size + self.n
            )
            self.bar(self.n / self.total)
            current_formatted = format_size(DOWNLOAD.downloaded_size)
            total_file_formatted = format_size(DOWNLOAD.total_size)

            rate = self.format_dict.get("rate")
            formatted_speed = f"{format_size(rate)}/s" if rate else "0 B/s"

            if rate and rate > 0:
                remaining_bytes = DOWNLOAD.total_size - DOWNLOAD.downloaded_size
                remaining_seconds = remaining_bytes / rate
                mins, secs = divmod(int(remaining_seconds), 60)
                hours, mins = divmod(mins, 60)
                if hours > 0:
                    eta = f"{hours:02d}:{mins:02d}:{secs:02d}"
                elif hours > 100:
                    eta = "--:--"
                else:
                    eta = f"{mins:02d}:{secs:02d}"
            else:
                eta = "--:--"
            formatted_stats = f"[{current_formatted}/{total_file_formatted}] ETA: {eta} ({formatted_speed})"

            self.bar.text(formatted_stats)

    def close(self):
        final_elapsed_seconds = self.format_dict.get("elapsed", 0.0)
        if hasattr(DOWNLOAD, "total_elapsed_time"):
            DOWNLOAD.total_elapsed_time += final_elapsed_seconds
        else:
            DOWNLOAD.total_elapsed_time = final_elapsed_seconds
        if self.manager:
            self.manager.__exit__(None, None, None)
    
    def display(self, *args, **kwargs):
        return

def pull_model(args):
    info("Starting model pull from hugging face")
    api = HfApi()
    try:
        files = api.list_repo_files(repo_id=f"{args.pull_model}")
        verbose(f"List of files on the repo: {files}")
        model_files = [file for file in files if file.endswith(".gguf") and not "mmproj" in file]
        mmproj_files = [file for file in files if "mmproj" in file or file.endswith(".mmproj")]
        verbose(f"Quantized model files: {model_files}")
        verbose(f"mmproj files: {mmproj_files}")
    except utils.RepositoryNotFoundError:
        error(f"No model found with the repo name {args.pull_model}")
        fatal("Aborting...")
    except (requests.exceptions.ConnectionError, ProtocolError) as e:
        error("Internet connection has been disconnected, Make sure you still have internet connection")
        fatal(f"Error information: {e}")
    except requests.exceptions.Timeout as e:
        error("The connection to the server was timed out!")
        fatal(f"Error information: {e}")
    except HfHubHTTPError as e:
        error("A hugging face server error has occured while performing the task")
        fatal(f"Error information: {e}")
    except requests.exceptions.RequestException as e:
        error("Generic connection error has occured!")
        fatal(f"Error information: {e}")
    except Exception as e:
        error("An unknown error has occured!")
        fatal(f"Error information: {e}")
    
    model_capabilities = [
        name for name, flag in[
            ("vision", args.vision),
            ("embedding", args.embedding),
            ("reranking", args.reranking),
        ]
        if flag
    ]
    verbose(f"Model capabilities: {model_capabilities}")

    quant_pattern = re.compile(r"\b(I?Q\d_\w+|BF16|F16|F32|MXFP4\w*)\b", re.IGNORECASE)

    model_file_metadata = {"model": "", "mmproj": ""}

    downloadable_models = {}
    for f in model_files:
        filename = f.split('/')[-1].removesuffix(".gguf")
        match = quant_pattern.search(filename)
        if not match:
            continue
        quant_type = match.group(1).upper()
        bit_match = re.search(r"\d+", quant_type)
        bit_size = bit_match.group() if bit_match else "16"
        key = f"{bit_size}-bit"
        downloadable_models.setdefault(key, {}).setdefault(quant_type, []).append(f)
    
    downloadable_mmproj = {}
    if mmproj_files:
        for f in mmproj_files:
            filename = f.split('/')[-1].removesuffix(".gguf" or ".mmproj")
            match = quant_pattern.search(filename)
            if not match:
                continue
            quant_type = match.group(1).upper()
            bit_match = re.search(r"\d+", quant_type)
            bit_size = bit_match.group() if bit_match else "16"
            key = f"{bit_size}-bit"
            downloadable_mmproj.setdefault(key, {}).setdefault(quant_type, []).append(f)

    verbose(f"Downloadable models: {downloadable_models}")
    verbose(f"Downloadable mmproj: {downloadable_mmproj}")
    ordered_downloadable_models = dict(sorted(downloadable_models.items(), key=lambda item: int(item[0].split('-')[0])))
    ordered_downloadable_mmproj = dict(sorted(downloadable_mmproj.items(), key=lambda item: int(item[0].split('-')[0])))

    print("\nAll available downloadable models: ")
    selection_download_models = {}
    list_numbers = 1
    default_selected_model = []
    for keys, value in ordered_downloadable_models.items():
        print(f"\n{keys}:")
        for num, quant in enumerate(value.keys(), start=list_numbers):
            file_list = value[quant]
            print(f"({num}). {quant}", end=" ")
            selection_download_models[list_numbers] = file_list
            if "Q4_K_M".lower() in quant.lower():
                default_selected_model = list_numbers
            list_numbers += 1
        print()
    print()
    if not default_selected_model:
        default_selected_model = 1
    verbose(f"Availalble selection for the models: {selection_download_models}")
    while True:
        try:
            user_choice_input = input(f"Select which model you want to download by the numbers (Default: {default_selected_model}): ")
            selected_model_number = default_selected_model if user_choice_input == "" else int(user_choice_input)
            break
        except ValueError:
            sys.stdout.write("\033[A\033[K")
            sys.stdout.flush()
    downloads_list = selection_download_models[selected_model_number]
    model_file_metadata["model"] = downloads_list[0]
    verbose(f"Selected model: {downloads_list}")

    if mmproj_files and args.vision:
        print("\nAll available downloadable mmproj: ")
        selection_download_mmproj = {}
        list_numbers = 1
        default_selected_mmproj = None
        for keys, value in ordered_downloadable_mmproj.items():
            print(f"\n{keys}:")
            for num, quant in enumerate(value.keys(), start=list_numbers):
                file_list = value[quant]
                print(f"({num}). {quant}", end=" ")
                selection_download_mmproj[list_numbers] = file_list
                if quant.lower() in downloads_list[0].lower() and not default_selected_mmproj:
                    default_selected_mmproj = list_numbers
                list_numbers += 1
            print()
        print()
        if not default_selected_mmproj:
            default_selected_mmproj = 1
        verbose(f"Availalble selection for the mmproj: {selection_download_mmproj}")
        while True:
            try:
                user_choice_input = input(f"Select which model you want to download by the numbers (Default: {default_selected_mmproj}): ")
                selected_mmproj_number = default_selected_mmproj if user_choice_input == "" else int(user_choice_input)
                break
            except ValueError:
                sys.stdout.write("\033[A\033[K")
                sys.stdout.flush()
        downloads_list += selection_download_mmproj[selected_mmproj_number]
        model_file_metadata["mmproj"] = " ".join(selection_download_mmproj[selected_mmproj_number])
    verbose(f"List of downloads: {downloads_list}")
    verbose(f"Metadata of the model will be: {model_file_metadata}")

    max_width_download_list = max(len(item) for item in downloads_list) + 5
    max_width_file_size = 20
    total_files_size = 0

    print(f"\nThe following files will be downloaded: ")
    print(f"{"File name":<{max_width_download_list + 5}}{"Size":<{max_width_file_size}}")
    print(f"{"":-^{max_width_download_list + max_width_file_size}}")
    for num, f in enumerate(downloads_list, start=1):
        file_url = hf_hub_url(repo_id=args.pull_model, filename=f)
        metadata = get_hf_file_metadata(file_url)
        total_files_size += metadata.size
        print(f"({num}). {f:<{max_width_download_list}}{format_size(metadata.size)}")
    
    print(f"{"Total download size":<{max_width_download_list + 5}}{format_size(total_files_size)}")
    print(f"\n{"Capabilities":<{max_width_download_list + 5}}{", ".join(model_capabilities) or "chat"}")
    
    while True:
        try:
            proceed_choice_input = input(f"Proceed installation for the following files? ([Y]/n): ")
            proceed_choice = "y" if proceed_choice_input == "" else str(proceed_choice_input)
            break
        except ValueError:
            sys.stdout.write("\033[A\033[K")
            sys.stdout.flush()

    
    if proceed_choice in ["y", "Y", "yes", "Yes", "YES"]:
        print("Proceeding with installation...")
    else:
        print("Installation cancelled...")
        return
    
    model_file_path = None
    mmproj_file_path = None
    DOWNLOAD.total_size = total_files_size
    DOWNLOAD.total_files = len(downloads_list)

    verbose(f"Using huggingface_hub {__version__}")
    for f in downloads_list:
        DOWNLOAD.current_filename = f
        try:
            downloaded_file_path = hf_hub_download(
                repo_id=args.pull_model,
                filename=f,
                tqdm_class=ProgressPipe
            )
        except (requests.exceptions.ConnectionError, ProtocolError) as e:
            error("Internet connection has been disconnected, Make sure you still have internet connection")
            fatal(f"Error information: {e}")
        except requests.exceptions.Timeout as e:
            error("The connection to the server was timed out!")
            fatal(f"Error information: {e}")
        except HfHubHTTPError as e:
            error("A hugging face server error has occured while performing the task")
            fatal(f"Error information: {e}")
        except requests.exceptions.RequestException as e:
            error("Generic connection error has occured!")
            fatal(f"Error information: {e}")
        except Exception as e:
            error("An unknown error has occured!")
            fatal(f"Error information: {e}")
        
        if model_file_metadata["model"] in f and not "mmproj" in f:
            model_file_path = downloaded_file_path
            model_file_name = f
            verbose(f"Model file name: {f}")
        elif model_file_metadata["mmproj"] in f and mmproj_files:
            mmproj_file_path = downloaded_file_path
            verbose(f"mmproj file name: {f}")
        file_url = hf_hub_url(repo_id=args.pull_model, filename=f)
        metadata = get_hf_file_metadata(file_url)
        DOWNLOAD.completed_size += metadata.size
        DOWNLOAD.current_file += 1
    
    verbose(f"Model file location: {model_file_path}, mmproj file location: {mmproj_file_path or ""}")

    model_data = {
        "id": model_file_name[:-5],
        "metadata": {
            "repo": args.pull_model,
            "commit_hash": Path(model_file_path).parent.name,
            "file": model_file_name,
            "path": model_file_path,
            "mmproj_path": mmproj_file_path or '',
            "created": int(time.time()),
            "capabilities": model_capabilities
        },
        "arguments": {
            "llama_args": ""
        },
    }
    verbose(f"Model data content: {model_data}")
    
    toml_path = Path(f"{MODELS_DIR_PATH}", f"{model_file_name[:-5]}.toml")
    write_toml(toml_path, model_data)
    print(f"\nModel {model_file_name[:-5]} successfully downloaded!\n")
    print(f"{"Model ID":<15}| {model_file_name[:-5]}")
    print(f"{"Repository":<15}| {args.pull_model}")
    print()
    print(f"{"Total size":<15}| {format_size(total_files_size)}")
    print(f"{"Elapsed time":<15}| {round(DOWNLOAD.total_elapsed_time, 2)} Sec")
    print(f"\nRun `gekoku serve {model_file_name[:-5]}` to initialize and use the model")
