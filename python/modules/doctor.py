import subprocess
import os
from utils.toml_manager import *
from utils.vars import CONFIG_DATA

def start_doctor():
    print("GekokuAI Doctor\n")
    cpu_backend = CONFIG_DATA["metadata"]["CPU_BACKEND"]
    gpu_backend = CONFIG_DATA["metadata"]["GPU_BACKEND"]
    cpu_name = subprocess.run("grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs", shell=True, capture_output=True, text=True)
    if gpu_backend == "CUDA":
        gpu_parse = subprocess.run(r"""lspci | grep -i "VGA\|3d" | grep -i "NVIDIA" | sed 's/.*\[//;s/\].*//' | head -n 1""", shell=True, capture_output=True, text=True)
    elif gpu_backend == "ROCm":
        gpu_parse = subprocess.run(r"""lspci | grep -i "VGA\|3d" | grep -i "AMD" | sed 's/.*\[//;s/\].*//' | head -n 1""", shell=True, capture_output=True, text=True)
    else:
        gpu_parse = "-"

    if gpu_parse == "-":
        gpu_name = "-"
    else:
        gpu_name = gpu_parse.stdout
    ram = subprocess.run(r"""free -m | awk '/^Mem:/{print $2}' | sed 's/Gi//'""", shell=True, capture_output=True, text=True)
    swap = subprocess.run(r"""free -m | awk '/^Swap:/{print $2}' | sed 's/Gi//'""", shell=True, capture_output=True, text=True)
    storage = subprocess.run(r"""df -m / | awk 'NR==2 {print $2}'""", shell=True, capture_output=True, text=True)
    used_storage = subprocess.run(r"""df -m / | awk 'NR==2 {print $3}'""", shell=True, capture_output=True, text=True)
    cpu_flags = subprocess.run(r"""grep -m 1 "flags" /proc/cpuinfo""", shell=True, capture_output=True, text=True)
    print(f"CPU: {cpu_name.stdout}\nGPU: {gpu_name}\nCPU Backend: {cpu_backend}\nGPU Backend: {gpu_backend}\nRam: {ram.stdout}\nSwap: {swap.stdout}\nStorage: {storage.stdout}\nUsed: {used_storage.stdout}\nCPU Flags: {cpu_flags.stdout}")
