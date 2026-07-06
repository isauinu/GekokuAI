#!/usr/bin/env bash

#Exit when a command dies
set -Eeuo pipefail
#DESCRIPTION
ver="v0.4"
date="$(date "+%F")"
author="ISAUINU"

#GLOBAL VARIABLES
GEKOKU_HOME="$HOME/.gekokuai"

#system
ARCH="$(uname -m)"
CPU_NAME="$(grep -m 1 'model name' /proc/cpuinfo | cut -d: -f2 | xargs)"
GPU_NAME="-"
RAM=$(free -m | awk '/^Mem:/{print $2}' | sed 's/Gi//')
SWAP=$(free -m | awk '/^Swap:/{print $2}' | sed 's/Gi//')
STORAGE=$(df -m / | awk 'NR==2 {print $2}')
USED_STORAGE=$(df -m / | awk 'NR==2 {print $3}')
CPU_FLAGS=$(grep -m 1 "flags" /proc/cpuinfo)
CPU_BACKEND="GENERIC"
GPU_BACKEND="CPU"
GPU_DRIVER_VERSION="-"
PACKAGE_MANAGER=""

#Requirements (Update these for any changes in the future)
REQUIRED_CPU_FLAGS=("sse4_1" "sse4_2")
RECOMMENDED_CPU_FLAGS=("avx" "avx2" "fma")
OPTIONAL_CPU_FLAGS=("avx512f" "avx512bw" "avx512vl" "avx512vnni" "amx_int8" "amx_bf16")
SUPPORTED_ROCM_ARCH=("gfx906" "gfx908" "gfx90a" "gfx1030" "gfx1100" "gfx1101" "gfx1102")
#Update these frequently depending by how many packages are needed
REQUIRED_PIP_PACKAGES=("pip" "setuptools" "wheel" "huggingface_hub" "tomli" "tomli-w" "fastapi[standard]" "uvicorn[standard]" "requests" "psutil" "tqdm" "alive-progress")
REQUIRED_DEPENDENCIES=("git" "cmake" "make" "gcc" "g++" "python3" "curl" "tar" "pip" "zip" "pkg-config" "node" "npm")
declare -A APT_DEPS=(
    ["git"]="git" 
    ["cmake"]="cmake" 
    ["make"]="make" 
    ["gcc"]="gcc" 
    ["g++"]="g++" 
    ["python3"]="python-is-python3"
    ["curl"]="curl" 
    ["tar"]="tar" 
    ["pip"]="pip" 
    ["zip"]="zip" 
    ["pkg-config"]="pkg-config"
    ["node"]="nodejs"
    ["npm"]="npm"
)
declare -A PACMAN_DEPS=(
    ["git"]="git" 
    ["cmake"]="cmake" 
    ["make"]="make" 
    ["gcc"]="gcc" 
    ["g++"]="gcc"
    ["python3"]="python3" 
    ["curl"]="curl" 
    ["tar"]="tar" 
    ["pip"]="python-pip" 
    ["zip"]="zip" 
    ["pkg-config"]="pkgconf"
    ["node"]="nodejs"
    ["npm"]="npm"
)
declare -A DNF_DEPS=(
    ["git"]="git" 
    ["cmake"]="cmake" 
    ["make"]="make" 
    ["gcc"]="gcc" 
    ["g++"]="gcc-g++" 
    ["python3"]="python3" 
    ["curl"]="curl" 
    ["tar"]="tar" 
    ["pip"]="python3-pip" 
    ["zip"]="zip" 
    ["pkg-config"]="pkgconf-pkg-config"
    ["node"]="nodejs"
    ["npm"]="npm"
)

cleanup() {
    tput cnorm
    # tput rmcup
    printf "\nEXITING...\n"
    sleep 2
    exit 0
}

exit_error() {
    tput cnorm

    printf "\nEXITING DUE TO ERROR...\n"
    exit 1
}

log() {
    local time="$(date "+%F %T")"
    local log_text=""
    #Check log use
    if [ "$#" -ge 2 ]; then
        log_text="$2"
    elif [ "$#" -ge 1 ]; then
        log_text="$1"
    else
        echo -e "[$time] \e[31m[Error] Incorrect use of log\e[0m"
        return 0
    fi
    #Then do log
    case "$1" in
        -f|--fatal) echo -e "[$time] \e[31m[FATAL] $log_text\e[0m"; exit_error ;;
        -e|--error) echo -e "[$time] \e[31m[Error] $log_text\e[0m" ;;
        -w|--warn) echo -e "[$time] \e[33m[Warn] $log_text\e[0m" ;;
        -s|--success) echo -e "[$time] \e[36m[Success] $log_text\e[0m" ;;
        -i|--info) echo -e "[$time] [Info] $log_text" ;;
        *) echo -e "[$time] [Log] $1" ;;
    esac
}

unexpected_error() {
    local code=$?
    local line=$1
    local error_type=""
    case "$code" in
        127) error_type="COMMAND_NOT_FOUND" ;;
        128) error_type="INVALID_EXIT_ARGUMENT";;
        126) error_type="PERMISSION_DENIED" ;;
        130) error_type="INTERRUPTED_BY_USER" ;;
        137) error_type="FORCEFULLY_KILLED" ;;
        1) error_type="GENERAL_ERROR" ;;
        2) error_type="INVALID_ARGUMENTS" ;;
        *) error_type="UNIDENTIFIED_ERROR" ;;
    esac

    log -f "Unexpected runtime error at line $line (code: $code $error_type) (command: $BASH_COMMAND)"
}

verifying_setup() {
    log -i "Verifying installation"
    test -d "$GEKOKU_HOME"
    test -d "$GEKOKU_HOME/venv"
    test -d "$GEKOKU_HOME/llama.cpp"
    log -s "GekokuAI successfully installed! have fun"
    cleanup
}

compile_environment() {
    #get script source
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    source_dir="${script_dir}/python"
    dest_dir="${GEKOKU_HOME}/app"
    log "SCRIPT DIR: $script_dir"
    log "SOURCE DIR: $source_dir"
    #Setup workspace
    log -i "Creating workspace"
    mkdir -p "$GEKOKU_HOME"
    mkdir -p "$GEKOKU_HOME/bin"
    mkdir -p "$GEKOKU_HOME/app"
    mkdir -p "$GEKOKU_HOME/models"
    mkdir -p "$GEKOKU_HOME/cache"
    mkdir -p "$GEKOKU_HOME/logs"
    mkdir -p "$GEKOKU_HOME/runtime"
    mkdir -p "$GEKOKU_HOME/config"
    mkdir -p "$GEKOKU_HOME/tmp"
    cp metadata.toml "$GEKOKU_HOME/"
    log -s "Workspace created successfully at $GEKOKU_HOME"

    #compiling llama cpp
    if [ -d "$GEKOKU_HOME/llama.cpp/.git" ]; then
        log -i "llama.cpp has already exists, updating instead"
        # git -C "$GEKOKU_HOME/llama.cpp" pull
    else
        log -i "Getting llama.cpp from source"
        git clone https://github.com/TheTom/llama-cpp-turboquant "$GEKOKU_HOME/llama.cpp"
        log -s "llama.cpp succesfully installed at $GEKOKU_HOME/llama.cpp"
    fi

    log -i "Compiling llama.cpp"
    cd "$GEKOKU_HOME/llama.cpp"
    local build_args=("-DCMAKE_BUILD_TYPE=Release" "-DGGML_NATIVE=ON" "-DLLAMA_BUILD_TESTS=OFF")
    # case "$CPU_BACKEND" in
    #     AVX512) build_args+=("-DGGML_AVX512=ON") ;;
    #     AVX2) build_args+=("-DGGML_AVX2=ON") ;;
    #     AVX) build_args+=("-DGGML_AVX=ON") ;;
    #     *) build_args+=("-DGGML_NATIVE=ON") ;;
    # esac
    case "$GPU_BACKEND" in
        CUDA) build_args+=("-DGGML_CUDA=ON") ;;
        ROCm) build_args+=("-DGGML_HIP=ON") ;;
        vulkan) build_args+=("-DGGML_VULKAN=ON") ;;
        *) : ;;
    esac
    cmake -B build "${build_args[@]}" . --log-level=VERBOSE
    log -s "Build configuration generated"
    sleep 0.5
    log -i "Building llama.cpp"
    cmake --build build -j$(nproc)
    log -s "Successfully building llama.cpp!"
    sleep 0.5
    log "Verifying llama.cpp existence"
    local result=$(find build -type f -executable | grep -i llama)
    if [ -n "$result" ]; then
        log -s "Found an llama.cpp build"
    else
        log -w "Unable to find existing llama.cpp build"
    fi
    sleep 0.2

    #Creating python environment
    log -i "Creating python environment"
    python3 -m venv "$GEKOKU_HOME/venv"
    log -s "Environment created"

    #Downloading needed python pip packages
    log -i "Installing pip packages"
    source "$GEKOKU_HOME/venv/bin/activate"
    log "Python: $(which python)"
    log "Python version: $(python --version)"
    log "PIP: $(which pip)"
    log "PIP version: $(pip --version)"
    python -m pip install --upgrade pip
    log "Installing ${REQUIRED_PIP_PACKAGES[@]}"
    pip install -U "${REQUIRED_PIP_PACKAGES[@]}"
    log "Exit code: $?"
    log -s "All needed packages are installed"
    sleep 0.3

    #Generating config file
    log -i "Generating default config file"
    local config_file="$GEKOKU_HOME/config/config.toml"
    cat << EOF > "$config_file"
# GekokuAI Configuration
[metadata]
CPU_BACKEND = "$CPU_BACKEND"
GPU_BACKEND = "$GPU_BACKEND"

[server]
host = "0.0.0.0"
port = 8080

[location]
workspace = "$GEKOKU_HOME"
models_path = "$GEKOKU_HOME/models"
venv_path = "$GEKOKU_HOME/venv"
log_path = "$GEKOKU_HOME/logs"
tmp_path = "$GEKOKU_HOME/tmp"

[llama_cpp]
llama_cpp_path = "$GEKOKU_HOME/llama.cpp"

[security]
host_managed_endpoints = false
allowed_hosts = ["127.0.0.1", "::1"]
EOF
    log -s "Successfully created config file at $config_file"
    log -i "Installing Gekoku to local user"
    if [ ! -d "$source_dir" ]; then
        log -f "Source directory doesn't exist, make sure the directory exist to complete setup..." 
        exit 1
    fi
    mkdir -p "$dest_dir"
    cp -R "$source_dir"/. "$dest_dir"
    log -s "Successfully installing Gekoku to local user"
    log -i "Creating gekoku command"
    local gekoku_file="$GEKOKU_HOME/bin/gekoku"
    cat << EOF > "$gekoku_file"
#!/usr/bin/env bash
exec "$GEKOKU_HOME/venv/bin/python" "$GEKOKU_HOME/app/main.py" "\$@"
EOF
    chmod +x "$gekoku_file"
    echo
    printf "\e[36mAdd the following to your shell:\e[0m "
    printf '\e[36mexport PATH="$HOME/.gekokuai/bin:$PATH"\e[0m'
    echo
    echo
    log -s "gekoku command created"
    sleep 1
    verifying_setup
}

install_missing_dependencies() {
    log -i "Installing missing dependencies"
    local packages_to_install=()
    for dep in "${missing_deps[@]}"; do
        if [ "$PACKAGE_MANAGER" == "apt-get" ]; then
            pkg="${APT_DEPS[$dep]:-}"
            if [[ -z "$pkg" ]]; then
                log -f "No package mapping found for dependency $dep"
            fi
            packages_to_install+=("$pkg")
        elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
            pkg="${PACMAN_DEPS[$dep]:-}"
            if [[ -z "$pkg" ]]; then
                log -f "No package mapping found for dependency $dep"
            fi
            packages_to_install+=("$pkg")
        elif [ "$PACKAGE_MANAGER" == "dnf" ]; then
            pkg="${DNF_DEPS[$dep]:-}"
            if [[ -z "$pkg" ]]; then
                log -f "No package mapping found for dependency $dep"
            fi
            packages_to_install+=("$pkg")
        else
            log -f "Please install the missing dependencies on your own!"
        fi
    done
    log "Packages to install: ${packages_to_install[*]}"
    if [ "$PACKAGE_MANAGER" == "apt-get" ]; then
        sudo apt-get update
        sudo apt-get install -y "${packages_to_install[@]}" python3-venv
    elif [ "$PACKAGE_MANAGER" == "pacman" ]; then
        sudo pacman -Sy
        sudo pacman -S "${packages_to_install[@]}" --noconfirm
    elif [ "$PACKAGE_MANAGER" == "dnf" ]; then
        sudo dnf update
        sudo dnf install -y "${packages_to_install[@]}"
    fi
    log -s "Missing dependencies are installed"
    log -i "re-checking any failed install"
    check_dependency
}

check_dependency() {
    missing_deps=()
    #Check Dependencies
    log -i "Checking Dependencies"

    for deps in "${REQUIRED_DEPENDENCIES[@]}"; do
        if command -v $deps >/dev/null 2>&1; then :
        else
            log -e "Dependency $deps is not installed"
            missing_deps+=("$deps")
        fi
    done

    if [ ${#missing_deps[@]} -eq 0 ]; then :
    else
        log "Missing required dependencies: $(
            for item in "${missing_deps[@]}"; do
                printf "$item "
            done
        )"
        log -i "The installer will install the missing dependencies"
        while true; do
            read -n 1 -p "proceed? [y/n] " choice
            echo
            case "$choice" in
                [yY]*)
                    install_missing_dependencies
                    return 0 ;;
                [nN]*) cleanup; ;;
                *) ;;
            esac
        done
    fi
    log -s "All dependencies needed are available"
    sleep 2
    compile_environment
}

check_system() {
    #Check Architecture
    log -i "Checking Architecture"

    case $ARCH in 
        x86_64|aarch64) ;;
        *) log -f "Architecture $ARCH is not supported" ;;
    esac
    log -s "Architecture used: $ARCH"

    #Check RAM and storage
    log -i "Checking Storage and Ram"

    local ram_min=8000
    local storage_left=$(($STORAGE - $USED_STORAGE))
    if (($RAM <= 8000)); then
        log -w "RAM Capacity is too low, running local LLMs might be affected"
    fi
    if (($storage_left <= 32000)); then
        log -e "STORAGE capacity is very low, some downloads might be affected"
    fi
    log -s "RAM: $RAM And STORAGE LEFT: $storage_left"

    #Check CPU Flags
    log -i "Checking CPU Flags"

    local fatal=0
    local has_flags=()

    #Determine CPU Backend for optimized llama cpp build
    determine_cpu_backend() {
        log "Supported CPU Flags: $(
            for item in "${has_flags[@]}"; do 
                printf "$item " 
            done 
        )"
        if [[ " ${has_flags[*]} " =~ " avx512f " ]] && [[ " ${has_flags[*]} " =~ " avx512bw " ]] && [[ " ${has_flags[*]} " =~ " avx512vl " ]]; then
            CPU_BACKEND="AVX512"
        elif [[ " ${has_flags[*]} " =~ " avx2 " ]] && [[ " ${has_flags[*]} " =~ " fma " ]]; then
            CPU_BACKEND="AVX2"
        elif [[ " ${has_flags[*]} " =~ " avx " ]]; then
            CPU_BACKEND="AVX"
        fi
        log -s "Using CPU Backend: $CPU_BACKEND"
    }
    #REQUIRED CHECK
    for flag in "${REQUIRED_CPU_FLAGS[@]}"; do
        if echo "$CPU_FLAGS" | grep -qiw "$flag"; then
            has_flags+=("$flag")
        else
            log -e "$flag is not a supported Flag"
            fatal=1
        fi
    done
    if [ "$fatal" -eq 1 ]; then
            log -f "Unsupported CPU Flags detected, cannot continue setup after this..."
    fi
    #RECCOMENDED CHECK
    for flag in "${RECOMMENDED_CPU_FLAGS[@]}"; do
        if echo "$CPU_FLAGS" | grep -qiw "$flag"; then
            has_flags+=("$flag")
        else
            log -w "$flag is not a supported Flag"
        fi
    done
    #OPTIONAL CHECK
    for flag in "${OPTIONAL_CPU_FLAGS[@]}"; do
        if echo "$CPU_FLAGS" | grep -qiw "$flag"; then
            has_flags+=("$flag")
        else
            log -w "$flag is not a supported Flag"
        fi
    done
    determine_cpu_backend

    #Check for GPU type
    log -i "Checking GPU Backend"

    if lspci | grep -qi "NVIDIA Corporation"; then
        GPU_NAME="$(lspci | grep -i "VGA\|3d" | grep -i "NVIDIA" | sed 's/.*\[//;s/\].*//' | head -n 1 )" #Thank you... google especially that sed... thing
        log -i "Using GPU: $GPU_NAME"
        if command -v nvidia-smi >/dev/null 2>&1; then
            GPU_DRIVER_VERSION=$(nvidia-smi --query-gpu=driver_version --format=csv,noheader)
            log -i "Driver version: $GPU_DRIVER_VERSION"
            if echo "$GPU_NAME" | grep -qiE "GeForce (210|310|610|GT 710|GT 730)|NVS"; then
                log -w "Detected GPU lacks CUDA microarchitecture support"
            else
                log -i "NVIDIA Proprietary drivers are available"
                if command -v nvcc >/dev/null 2>&1; then
                    GPU_BACKEND="CUDA"
                else
                    log -f "No CUDA toolkit is detected on the current system, it is better to install it yourself first before continuing"
                fi
                
            fi
        else
            log -e "No NVIDIA Proprietary drivers found. If you're using an open-source driver, CUDA Simply won't work"
        fi
    elif lspci | grep -qi "Advanced Micro Devices.*\[AMD/ATI\]"; then
        local rocm_support=0
        GPU_NAME="$(lspci | grep -i "VGA\|3d" | grep -i "AMD" | sed 's/.*\[//;s/\].*//' | head -n 1 )"
        log -i "Using GPU: $GPU_NAME"
        if command -v rocminfo >/dev/null 2>&1; then
            GPU_DRIVER_VERSION=$(rocminfo | grep -oE "gfx[0-9]+" | head -n 1)
            for arch in "${SUPPORTED_ROCM_ARCH[@]}"; do
                if [[ "$GPU_DRIVER_VERSION" == "$arch" ]]; then
                    GPU_BACKEND="ROCm"
                    log -i "AMD Proprietary driver and ROCm Support are available"
                    rocm_support=1
                    break
                fi
            done
            if [ "$rocm_support" -eq 0 ]; then
                log -w "ROCm is available. However, architecture $GPU_DRIVER_VERSION might not support it natively"
            fi
        else
            log -e "No ROCm utilities found"
        fi
    elif command -v vulkaninfo >/dev/null 2>&1; then
        if vulkaninfo --summary 2>/dev/null | grep -qi "deviceType.*gpu"; then
            log -i "Universal Vulkan Graphics API are available"
            GPU_BACKEND="vulkan"
        fi
    else
        log -e "No Hardware compute runtimes available to use. Everything will be SO SLOW, good luck"
    fi
    log -s "Using GPU Backend: $GPU_BACKEND"

    #Used package manager
    log -i "Checking used package manager"
    if command -v "apt-get" >/dev/null 2>&1; then
        PACKAGE_MANAGER="apt-get"
    elif command -v "pacman" >/dev/null 2>&1; then
        PACKAGE_MANAGER="pacman"
    elif command -v "dnf" >/dev/null 2>&1; then
        PACKAGE_MANAGER="dnf"
    else
        log -e "No package manager detected (?)"
    fi
    log -s "Using Package Manager: $PACKAGE_MANAGER"

    echo
    log -i "SYSTEM OVERVIEW:"
    printf " System Architecture: $ARCH \n CPU: $CPU_NAME \n GPU: $GPU_NAME \n STORAGE: ${STORAGE}M (Used: ${USED_STORAGE}M) \n RAM: ${RAM}M \n SWAP: ${SWAP}M \n CPU BACKEND: $CPU_BACKEND \n GPU BACKEND: $GPU_BACKEND \n GPU DRIVER VERSION: $GPU_DRIVER_VERSION \n\n"
    sleep 2
    check_dependency
}

main() {
    trap cleanup INT
    trap 'unexpected_error $LINENO' ERR

    printf "GekokuAI $ver\n$date\n$author\n\n\n"

    sleep 2
    check_system
}

main