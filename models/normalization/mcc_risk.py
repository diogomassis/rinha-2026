import json
import os

class MccRiskConfig:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, filepath):
        if MccRiskConfig._initialized:
            return
            
        self.filepath = filepath
        self._raw_data = {}
        self.load_config()
        MccRiskConfig._initialized = True

    def load_config(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Configuration file {self.filepath} not found.")
            
        with open(self.filepath, 'r') as file:
            self._raw_data = json.load(file)
        print(f"Mcc Risk: loaded {len(self._raw_data)} items.")
        for key, value in self._raw_data.items():
            setattr(self, f"mcc_{key}", value)

    def __getitem__(self, key):
        return self._raw_data.get(str(key))

    def get(self, key, default=None):
        return self._raw_data.get(str(key), default)
    