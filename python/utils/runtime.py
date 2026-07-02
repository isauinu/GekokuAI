from utils.logger import *

class RunningModel:
    def __init__(self):
        self.model = None
        self.process = None
        self.pid = None
        self.port = None

class Runtime:
    def __init__(self):
        self.running = False
        self.pid = None
        self.host = None
        self.port = None
        self.running_models = {}
        self.log_file = None