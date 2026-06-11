try:
    import tomlib
except ImportError:
    import tomli as tomlib
import tomli_w

def read_toml(file_path): # File path only
    with open(file_path, "rb") as f:
        return tomlib.load(f)
    
def write_toml(file_path, data): # File path then data
    with open(file_path, "wb") as f:
        tomli_w.dump(data, f)