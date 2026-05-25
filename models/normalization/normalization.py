import json
import os

class NormalizationConfig:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, filepath):
        if NormalizationConfig._initialized:
            return
            
        self.filepath = filepath
        self.load_config()
        NormalizationConfig._initialized = True

    def load_config(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"Configuration file {self.filepath} not found.")
            
        with open(self.filepath, 'r') as file:
            data = json.load(file)
        print(f"Normalization: loaded {len(data)} items.") 
        for key, value in data.items():
            setattr(self, key, value)
