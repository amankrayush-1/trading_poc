import json
from pathlib import Path
from typing import Dict, Any


class ConfigReader:
   
    def __init__(self, config_path: str = "bot/config.json"):
        self.config_path = config_path
        self.config = self.read_config()
    
    def read_config(self) -> Dict[str, Any]:
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        with open(config_file, 'r') as f:
            config = json.load(f)
        
        return config

    
    def get_strategy_config(self, strategy_name: str) -> Dict[str, Any]:
        if strategy_name not in self.config:
            raise KeyError(f"Strategy '{strategy_name}' not found in configuration")
        
        return self.config[strategy_name]
    
    def get_active_strategy_config(self) -> tuple[str, Dict[str, Any]]:
        if 'strategy' not in self.config:
            raise KeyError("'strategy' key not found in configuration")
        
        active_strategy = self.config['strategy']
        strategy_config = self.get_strategy_config(active_strategy)
        
        return active_strategy, strategy_config
    
    def get_config_value(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)
    
    def get_all_config(self) -> Dict[str, Any]:
        return self.config

