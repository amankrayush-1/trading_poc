"""
SOR (Sell on Rise) Main Execution Script
This script initializes and runs the SOR trading strategy
Supports simultaneous execution across multiple accounts using threading
"""

import sys
from pathlib import Path
from threading import Thread
from typing import Dict, Any, List

# Add parent directory to path to import bot.utils
sys.path.append(str(Path(__file__).parent.parent.parent))

from growwapi import GrowwAPI
from bot.utils import Utils
from bot.sor.config_reader import ConfigReader
from bot.sor.strategy import SORStrategy


def execute_strategy_for_account(account: Dict[str, Any], config: Dict[str, Any], results: List[Dict[str, Any]]):
    """
    Execute strategy for a single account (thread worker function)
    
    Args:
        account: Account configuration dictionary
        config: Global configuration dictionary
        results: Shared list to store results
    """
    account_name = account.get('name', 'Unknown')
    print(f"\n{'=' * 80}")
    print(f"EXECUTING STRATEGY FOR ACCOUNT: {account_name}")
    print(f"{'=' * 80}")
    
    try:
        # Initialize Groww API
        groww = GrowwAPI(
            token=account.get('token'),
            secret=account.get('secret')
        )
        
        # Initialize Utils
        utils = Utils(groww)
        
        # Override number_of_lots if specified in account config
        account_config = config.copy()
        if 'number_of_lots' in account:
            account_config['number_of_lots'] = account['number_of_lots']
            print(f"Using account-specific lots: {account['number_of_lots']}")
        
        # Initialize and execute strategy
        strategy = SORStrategy(groww, utils, account_config)
        result = strategy.execute()
        
        # Store result
        results.append({
            'account': account_name,
            'result': result
        })
        
        print(f"\n--- Execution Result for {account_name} ---")
        print(f"Status: {result.get('status')}")
        print(f"Action: {result.get('action')}")
        if result.get('case'):
            print(f"Case: {result.get('case')}")
        if result.get('trigger'):
            print(f"Trigger: {result.get('trigger')}")
        if result.get('strike'):
            print(f"Strike: {result.get('strike')}")
        if result.get('quantity'):
            print(f"Quantity: {result.get('quantity')}")
        if result.get('error'):
            print(f"Error: {result.get('error')}")
        
    except Exception as e:
        print(f"\n✗ Error executing strategy for {account_name}: {e}")
        import traceback
        traceback.print_exc()
        results.append({
            'account': account_name,
            'result': {
                'status': 'error',
                'error': str(e)
            }
        })


def main():
    """
    Main execution function for SOR bot
    """
    try:
        print("=" * 80)
        print("SOR (SELL ON RISE) - TRADING STRATEGY")
        print("=" * 80)
        
        # Read configuration
        config_path = Path(__file__).parent / "config.json"
        config_reader = ConfigReader(str(config_path))
        config = config_reader.get_all_config()
        
        print("\n--- Configuration Loaded ---")
        print(f"Exchange: {config.get('exchange')}")
        print(f"Trading Symbol: {config.get('trading_symbol')}")
        print(f"Expiry to Trade: {config.get('expiry_to_trade')}")
        print(f"Spread Gap: {config.get('spread_gap')}")
        print(f"Number of Lots: {config.get('number_of_lots')}")
        print(f"Lot Size: {config.get('lot_size')}")
        print(f"ITM Points: {config.get('itm_points')}")
        print(f"ATR: {config.get('atr')}")
        
        # Get enabled accounts
        accounts = config.get('accounts', [])
        enabled_accounts = [acc for acc in accounts if acc.get('enabled', False)]
        
        if not enabled_accounts:
            print("\n✗ No enabled accounts found in configuration")
            return
        
        print(f"\n--- Found {len(enabled_accounts)} Enabled Account(s) ---")
        print(f"--- Executing strategies SIMULTANEOUSLY across all accounts ---")
        
        # Execute strategy for each enabled account using threads for simultaneous execution
        results = []
        threads = []
        
        # Create and start a thread for each account
        for account in enabled_accounts:
            thread = Thread(
                target=execute_strategy_for_account,
                args=(account, config, results)
            )
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        print(f"\n--- All account executions completed ---")
        
        # Print summary
        print(f"\n{'=' * 80}")
        print("EXECUTION SUMMARY")
        print(f"{'=' * 80}")
        
        for result_data in results:
            account_name = result_data['account']
            result = result_data['result']
            status = result.get('status')
            action = result.get('action', 'N/A')
            
            print(f"\n{account_name}:")
            print(f"  Status: {status}")
            print(f"  Action: {action}")
            
            if status == 'success' and action != 'no_trade':
                print(f"  ✓ Trade executed successfully")
            elif status == 'success' and action == 'no_trade':
                print(f"  ℹ No trade conditions met")
            else:
                print(f"  ✗ Execution failed")
        
        print(f"\n{'=' * 80}")
        print("SOR BOT EXECUTION COMPLETED")
        print(f"{'=' * 80}\n")
        
    except Exception as e:
        print(f"\n✗ Fatal error in main execution: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
