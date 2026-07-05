from utils.globals import GEKOKUAI_VERSION, CONFIG_DATA, GEKOKUAI_BUILD_RELEASE_DATE, GEKOKUAI_LICENSE
import platform
from huggingface_hub import __version__

def program_info():
    gekokuai_internal_info = [CONFIG_DATA["location"]["workspace"], CONFIG_DATA["location"]["models_path"], CONFIG_DATA["llama_cpp"]["llama_cpp_path"]]
    max_width = max(len(item) for item in gekokuai_internal_info) + 5
    print(f"GekokuAI {GEKOKUAI_VERSION}\n")
    print(f"{"Information":-^{max_width*2+2}}")
    print()
    print(f"{"Version":<{max_width}}| {GEKOKUAI_VERSION}")
    print(f"{"Release date":<{max_width}}| {GEKOKUAI_BUILD_RELEASE_DATE}")
    print(f"{"License":<{max_width}}| {GEKOKUAI_LICENSE}")
    print()
    print(f"{"Python":<{max_width}}| {platform.python_version()}")
    print(f"{"Hugging face":<{max_width}}| {__version__}")
    print(f"{"Platform":<{max_width}}| {f"{platform.system()} {platform.machine()}"}")
    print()
    print(f"{"Workspace":<{max_width}}| {CONFIG_DATA["location"]["workspace"]}")
    print(f"{"Models metadata":<{max_width}}| {CONFIG_DATA["location"]["models_path"]}")
    print(f"{"llama.cpp path":<{max_width}}| {CONFIG_DATA["llama_cpp"]["llama_cpp_path"]}")
    print()
    print("Run `gekoku --help` to view all commands")
    print("Run `gekoku doctor` to verify your installation")