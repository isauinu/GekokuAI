from tqdm.auto import tqdm

class DownloadMetadata:
    def __init__(self):
        self.total_size = 0
        self.downloaded_size = 0
        
        self.completed_size = 0

        self.current_file = 1
        self.total_files = 1

        self.current_filename = ""
        self.total_elapsed_time = 0