"""
Configuration Reader for SOR Bot
Reads and validates configuration from config.json
"""

import json
from typing import Dict, Any, List


class ConfigReader:
    """
    Configuration reader class for SOR bot
    """
    
    def __init__(self, config_path: str):
        """
        Initialize the config reader
        
        Args:
            config_path: Path to the config.json file
        """
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Returns:
            Dictionary containing configuration
        """
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            return config
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file not found: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def get_all_config(self) -> Dict[str, Any]:
        """
        Get all configuration
        
        Returns:
            Complete configuration dictionary
        """
        return self.config
    
    def get_accounts(self) -> List[Dict[str, Any]]:
        """
        Get list of accounts from configuration
        
        Returns:
            List of account dictionaries
        """
        return self.config.get('accounts', [])
    
    def get_enabled_accounts(self) -> List[Dict[str, Any]]:
        """
        Get list of enabled accounts
        
        Returns:
            List of enabled account dictionaries
        """
        accounts = self.get_accounts()
        return [acc for acc in accounts if acc.get('enabled', False)]
