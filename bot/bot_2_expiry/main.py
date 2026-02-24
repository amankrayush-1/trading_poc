"""
Bot 2 - Standalone Trading Bot
Entry point for Bot 2 with G1, G2, R1 level-based strategy
"""

import sys
import os
import json
from typing import Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from growwapi import GrowwAPI

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bot.bot_2_expiry.strategy import Bot2Strategy
from bot.utils import Utils


class Bot2Driver:
    """
    Main driver class for Bot 2
    Responsible for:
    - Reading configuration from bot_2_expiry/config.json
    - Initializing and running the strategy across multiple accounts in parallel
    """
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the bot driver
        
        Args:
            config_path: Path to the configuration file
        """
        # Resolve config path relative to this file's directory
        if not os.path.isabs(config_path):
            config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_path)
        
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """
        Load configuration from JSON file
        
        Returns:
            Configuration dictionary
        """
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            print(f"✓ Configuration loaded from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"✗ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON in configuration file: {e}")
            sys.exit(1)
    
    def initialize_groww_api(self, name: str, token: str) -> GrowwAPI:
        """
        Initialize Groww API for an account
        
        Args:
            name: Account name
            token: API token
            
        Returns:
            GrowwAPI instance or None if failed
        """
        try:
            groww = GrowwAPI(token)
            print(f"✓ Groww API initialized for {name}'s account")
            return groww
        except Exception as e:
            print(f"✗ Failed to initialize Groww API for {name}: {e}")
            return None
    
    def execute_strategy_for_account(self, account: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute strategy for a single account
        
        Args:
            account: Account configuration dictionary
            
        Returns:
            Dictionary with execution results for this account
        """
        account_name = account.get('name', 'Unknown')
        
        try:
            print(f"\n[{account_name}] Starting Bot 2 strategy execution...")
            
            # Initialize Groww API for this account
            groww = self.initialize_groww_api(account_name, account.get('token'))
            
            if groww is None:
                return {
                    "account": account_name,
                    "status": "error",
                    "error": "Failed to initialize Groww API"
                }
            
            # Create utils instance
            utils = Utils(groww)
            
            # Create account-specific config by merging global config with account-specific overrides
            account_config = self.config.copy()
            
            # Override number_of_lots if specified at account level
            if 'number_of_lots' in account:
                account_config['number_of_lots'] = account['number_of_lots']
                print(f"[{account_name}] Using account-specific number_of_lots: {account['number_of_lots']}")
            
            # Instantiate the strategy with account-specific config
            strategy_instance = Bot2Strategy(
                groww=groww,
                utils=utils,
                config=account_config
            )
            
            print(f"[{account_name}] ✓ Bot 2 Strategy loaded")
            
            # Execute the strategy
            result = strategy_instance.execute()
            result['account'] = account_name
            
            print(f"[{account_name}] ✓ Strategy execution completed")
            return result
            
        except Exception as e:
            print(f"[{account_name}] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "account": account_name,
                "status": "error",
                "error": str(e)
            }
    
    def run(self, max_workers: int = None):
        """
        Execute strategy across multiple accounts in parallel
        
        Args:
            max_workers: Maximum number of parallel threads (default: number of accounts)
            
        Returns:
            List of results from all accounts
        """
        try:
            # Get accounts from config
            accounts = self.config.get('accounts', [])
            
            if not accounts:
                print("✗ No accounts configured in config.json")
                return []
            
            # Filter enabled accounts
            enabled_accounts = [acc for acc in accounts if acc.get('enabled', True)]
            
            if not enabled_accounts:
                print("✗ No enabled accounts found")
                return []
            
            print(f"\nFound {len(enabled_accounts)} enabled account(s)")
            print("=" * 50)
            
            # Set max_workers to number of accounts if not specified
            if max_workers is None:
                max_workers = len(enabled_accounts)
            
            results = []
            
            # Execute strategy in parallel across all accounts
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # Submit all tasks
                future_to_account = {
                    executor.submit(self.execute_strategy_for_account, account): account 
                    for account in enabled_accounts
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_account):
                    account = future_to_account[future]
                    try:
                        result = future.result()
                        results.append(result)
                    except Exception as e:
                        print(f"✗ Exception for account {account.get('name')}: {e}")
                        results.append({
                            "account": account.get('name'),
                            "status": "error",
                            "error": str(e)
                        })
            
            print("\n" + "=" * 50)
            print("EXECUTION SUMMARY")
            print("=" * 50)
            
            # Print summary
            for result in results:
                account_name = result.get('account', 'Unknown')
                status = result.get('status', 'unknown')
                action = result.get('action', 'N/A')
                
                if status == "success":
                    print(f"✓ {account_name}: {status.upper()} - {action}")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"✗ {account_name}: {status.upper()} - {error}")
            
            return results
            
        except Exception as e:
            print(f"✗ Error during bot execution: {e}")
            import traceback
            traceback.print_exc()
            return []


def main():
    """
    Entry point for Bot 2
    """
    print("=" * 50)
    print("Bot 2 - G1/G2/R1 Level Strategy (Parallel Mode)")
    print("=" * 50)
    
    # Create the bot driver
    driver = Bot2Driver()
    
    # Run strategy across all accounts in parallel
    results = driver.run()
    
    # Check if all executions were successful
    success = all(result.get('status') == 'success' for result in results)
    
    if success and results:
        print("\n✓ Bot 2 execution completed successfully for all accounts")
        sys.exit(0)
    elif results:
        print("\n⚠ Bot 2 execution completed with some errors")
        sys.exit(1)
    else:
        print("\n✗ Bot 2 execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
