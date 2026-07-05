def format_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(size)
    for unit in units:
        if size < 1024 or unit == units[-1]:
            return f"{size:.2f} {unit}"
        size /= 1024