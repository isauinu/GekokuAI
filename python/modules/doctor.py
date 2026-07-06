import subprocess
from utils.toml_manager import *
from utils.globals import CONFIG_DATA, VENV_PYTHON, GEKOKU_HOME, CONFIG_PATH, MODELS_DIR_PATH
import sys
import platform
from pathlib import Path
from utils.toml_manager import *
import ipaddress
from utils.logger import *

results = {
    "success_result": 0,
    "warning_result": 0,
    "failure_result": 0
}

def passed():
    print(" (Passed)")
    results["success_result"] += 1

def warning():
    print(" (Warning)")
    results["warning_result"] += 1

def failed():
    print(" (Failed)")
    results["failure_result"] += 1

def doctor_normal(args):

    max_width = 20
    print("GekokuAI Doctor\n")

    print(f"{"Python":<{max_width}}| {platform.python_version()}", end="")
    if sys.version_info >= (3, 11):
        passed()
    elif sys.version_info >= (3, 8):
        warning()
    else:
        failed()
    
    print(f"{"Virtual environment":<{max_width}}| {VENV_PYTHON}", end="")
    if sys.executable == VENV_PYTHON:
        passed()
    else:
        failed()

    print(f"{"Workspace":<{max_width}}| {CONFIG_DATA["location"]["workspace"]}", end="")
    if Path(CONFIG_DATA["location"]["workspace"]).is_dir():
        passed()
    else:
        failed()

    print(f"{"Configuration":<{max_width}}| {CONFIG_PATH}", end="")
    if Path(CONFIG_PATH).is_file():
        try:
            read_toml(CONFIG_PATH)
            passed()
        except Exception as e:
            warning()
            verbose(f"Exception during the current test: {e}")
    else:
        failed()

    print(f"{"Metadata":<{max_width}}| {Path(GEKOKU_HOME, "metadata.toml")}", end="")
    if Path(GEKOKU_HOME, "metadata.toml").is_file():
        try:
            read_toml(Path(GEKOKU_HOME, "metadata.toml"))
            passed()
        except Exception as e:
            warning()
            verbose(f"Exception during the current test: {e}")
    else:
        failed()

    print(f"{"Models directory":<{max_width}}| {MODELS_DIR_PATH}", end="")
    if Path(MODELS_DIR_PATH).is_dir():
        passed()
    else:
        failed()
    
    print(f"{"llama.cpp":<{max_width}}| {Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"])}", end="")
    if Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"]).is_dir():
        passed()
    else:
        failed()

    try:
        result = subprocess.run([Path(CONFIG_DATA["llama_cpp"]["llama_cpp_path"], "build", "bin", "llama-cli"), "--version"], 
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT, 
            text=True, 
        )
        print(f"{"llama.cpp bin":<{ max_width}}| {result.stdout.split("\n")[0].strip()}", end="")
        passed()
    except Exception as e:
        result = "unknown"
        print(f"{"llama.cpp bin":<{ max_width}}| {result}", end="")
        failed()
        verbose(f"Exception during the current test: {e}")

    try:
        import huggingface_hub
        print(f"{"Hugging face":<{ max_width}}| {huggingface_hub.__version__}", end="")
        passed()
    except Exception as e:
        print(f"{"Hugging face":<{ max_width}}| unknown", end="")
        failed()
        verbose(f"Exception during the current test: {e}")

    try:
        cpu_name = subprocess.run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs", shell=True, capture_output=True, text=True)
        print(f"{"CPU":<{ max_width}}| {cpu_name.stdout.strip()}", end="")
        passed()
    except Exception as e:
        print(f"{"CPU":<{ max_width}}| unknown", end="")
        failed()
        verbose(f"Exception during the current test: {e}")

    try:
        gpu_backend = CONFIG_DATA["metadata"]["GPU_BACKEND"]
        if gpu_backend == "CUDA":
            gpu_parse = subprocess.run(r"""lspci | grep -i "VGA\|3d" | grep -i "NVIDIA" | sed 's/.*\[//;s/\].*//' | head -n 1""", shell=True, capture_output=True, text=True)
        elif gpu_backend == "ROCm":
            gpu_parse = subprocess.run(r"""lspci | grep -i "VGA\|3d" | grep -i "AMD" | sed 's/.*\[//;s/\].*//' | head -n 1""", shell=True, capture_output=True, text=True)
        elif gpu_backend == "vulkan":
            gpu_parse = subprocess.run('vulkaninfo --summary 2>/dev/null | grep -i "deviceName"', shell=True, capture_output=True, text=True)
        else:
            gpu_parse = "-"
        if gpu_parse != "-":
            print(f"{"GPU":<{max_width}}| ({gpu_backend}) {gpu_parse.stdout.split('=', 1)[-1].strip()}", end="")
            passed()
        else:
            print(f"{"GPU":<{max_width}}| cpu", end="")
            warning()
    except Exception as e:
        print(e)
        print(f"{"GPU":<{ max_width}}| unknown", end="")
        failed()
        verbose(f"Exception during the current test: {e}")

    try:
        print(f"{"Daemon host":<{max_width}}| {CONFIG_DATA["server"]["host"]}", end="")
        ipaddress.ip_address(CONFIG_DATA["server"]["host"])
        passed()
    except ValueError as e:
        print(f"{"Daemon host":<{max_width}}| unknown", end="")
        failed()
        verbose(f"Exception during the current test: {e}")
    
    try:
        print(f"{"Daemon port":<{max_width}}| {CONFIG_DATA["server"]["port"]}", end="")
        if isinstance(CONFIG_DATA["server"]["port"], int):
            passed()
        else:
            failed()
    except Exception as e:
        failed()
        verbose(f"Exception during the current test: {e}")

    doctor_result(results)


def doctor_result(results):
    print()
    max_result_width = 20
    print(f"{"Passed":<{max_result_width}}{"Warning":<{max_result_width}}{"Failed":<{max_result_width}}")
    print(f"{"":-^{max_result_width * 3}}")
    print(f"{results["success_result"]:<{max_result_width}}{results["warning_result"]:<{max_result_width}}{results["failure_result"]:<{max_result_width}}")