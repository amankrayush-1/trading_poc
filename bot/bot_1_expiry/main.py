"""
Bot Driver/Main Class
This module serves as the entry point for the trading bot.
It reads the configuration, determines which strategy to use, and executes it across multiple accounts in parallel.
"""

import sys
import os
from typing import Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from growwapi import GrowwAPI

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from bot.bot_1_expiry.config_reader import ConfigReader
from bot.utils import Utils
from bot.bot_1_expiry.sell_1.strategy import Sell1Strategy
from bot.bot_1_expiry.sell_2.strategy import Sell2Strategy
from bot.bot_1_expiry.sell_3.strategy import Sell3Strategy
from bot.bot_1_expiry.sell_4.strategy import Sell4Strategy
from bot.bot_1_expiry.sell_5.strategy import Sell5Strategy
from bot.bot_1_expiry.buy_1.strategy import Buy1Strategy


class BotDriver:
    """
    Main driver class for the trading bot.
    Responsible for:
    - Reading configuration
    - Determining which strategy to execute
    - Initializing and running the selected strategy across multiple accounts in parallel
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
        
        self.config_reader = ConfigReader(config_path)
        self.config = self.config_reader.get_all_config()
        
    def initialize_groww_api(self, name: str, token: str) -> Optional[GrowwAPI]:
        try:
            groww = GrowwAPI(token)
            print(f"✓ Groww API initialized for {name}'s account")
            return groww
        except Exception as e:
            print(f"✗ Failed to initialize Groww API: {e}")
            return None
    
    def get_strategy_class(self, strategy_name: str):
        """
        Factory method to get the strategy class based on strategy name
        
        Args:
            strategy_name: Name of the strategy (e.g., 'sell_1', 'sell_2')
            
        Returns:
            Strategy class or None if not found
        """
        if strategy_name == "sell_1":
            return Sell1Strategy
        elif strategy_name == "sell_2":
            return Sell2Strategy
        elif strategy_name == "sell_3":
            return Sell3Strategy
        elif strategy_name == "sell_4":
            return Sell4Strategy
        elif strategy_name == "sell_5":
            return Sell5Strategy
        elif strategy_name == "buy_1":
            return Buy1Strategy
        else:
            print(f"✗ Unknown strategy: '{strategy_name}'")
            return None
    
    def execute_strategy_for_account(self, account: Dict[str, Any], strategy_name: str, 
                                     strategy_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute strategy for a single account
        
        Args:
            account: Account configuration dictionary
            strategy_name: Name of the strategy to execute
            strategy_config: Strategy-specific configuration
            
        Returns:
            Dictionary with execution results for this account
        """
        account_name = account.get('name', 'Unknown')
        
        try:
            print(f"\n[{account_name}] Starting strategy execution...")
            
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
            
            # Get the strategy class
            strategy_class = self.get_strategy_class(strategy_name)
            
            if strategy_class is None:
                return {
                    "account": account_name,
                    "status": "error",
                    "error": f"Strategy '{strategy_name}' not found"
                }
            
            # Instantiate the strategy
            strategy_instance = strategy_class(
                groww=groww,
                utils=utils,
                config=self.config,
                strategy_config=strategy_config
            )
            
            print(f"[{account_name}] ✓ Strategy '{strategy_name}' loaded")
            
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
    
    def run(self, max_workers: Optional[int] = None):
        """
        Execute strategy across multiple accounts in parallel
        
        Args:
            max_workers: Maximum number of parallel threads (default: number of accounts)
            
        Returns:
            List of results from all accounts
        """
        try:
            # Get active strategy name and config
            active_strategy, strategy_config = self.config_reader.get_active_strategy_config()
            print(f"Active Strategy: {active_strategy}")
            print(f"Strategy Config: {strategy_config}")
            
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
                    executor.submit(
                        self.execute_strategy_for_account,
                        account,
                        active_strategy,
                        strategy_config
                    ): account for account in enabled_accounts
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
            
        except KeyError as e:
            print(f"✗ Configuration error: {e}")
            return []
        except Exception as e:
            print(f"✗ Error during bot execution: {e}")
            import traceback
            traceback.print_exc()
            return []


def main():
    """
    Entry point for the bot
    """
    print("=" * 50)
    print("Trading Bot - Starting (Parallel Mode)")
    print("=" * 50)
    
    # Create the bot driver
    driver = BotDriver()
    
    # Run strategy across all accounts in parallel
    results = driver.run()
    
    # Check if all executions were successful
    success = all(result.get('status') == 'success' for result in results)
    
    if success and results:
        print("\n✓ Bot execution completed successfully for all accounts")
        sys.exit(0)
    elif results:
        print("\n⚠ Bot execution completed with some errors")
        sys.exit(1)
    else:
        print("\n✗ Bot execution failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
