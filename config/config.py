# config.py
import json

class Config:
    def __init__(self, config_path='config/config.json'):
        self.config_path = config_path
        self.load_config()

    def load_config(self):
        with open(self.config_path, 'r') as f:
            config_data = json.load(f)
            self.__dict__.update(config_data)

    def save_config(self):
        with open(self.config_path, 'w') as f:
            json.dump(self.__dict__, f, indent=4)

    def __getitem__(self, item):
        return self.__dict__.get(item)

    def __setitem__(self, key, value):
        self.__dict__[key] = value
        self.save_config()

# Instantiate a global config object
config = Config()
