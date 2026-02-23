"""
Test script to verify the get_spot_price method in Utils class
"""
from growwapi import GrowwAPI
from bot.utils import Utils
from bot.config_reader import ConfigReader

def test_get_spot_price():
    """Test getting spot prices for NSE and BSE"""
    
    # Read config
    config = ConfigReader('bot/config.json')
    
    # Get first enabled account
    enabled_accounts = [acc for acc in config.accounts if acc['enabled']]
    if not enabled_accounts:
        print("No enabled accounts found in config")
        return
    
    account = enabled_accounts[0]
    print(f"Testing with account: {account['name']}")
    
    # Initialize Groww API
    groww = GrowwAPI(account['token'])
    utils = Utils(groww)
    
    # Test NSE - NIFTY 50
    print("\n=== Testing NSE (NIFTY 50) ===")
    try:
        nifty_price = utils.get_spot_price('NSE')
        print(f"✓ NIFTY 50 LTP: ₹{nifty_price}")
    except Exception as e:
        print(f"✗ Error getting NIFTY price: {e}")
    
    # Test BSE - SENSEX
    print("\n=== Testing BSE (SENSEX) ===")
    try:
        sensex_price = utils.get_spot_price('BSE')
        print(f"✓ SENSEX LTP: ₹{sensex_price}")
    except Exception as e:
        print(f"✗ Error getting SENSEX price: {e}")
    
    # Test with lowercase
    print("\n=== Testing with lowercase 'nse' ===")
    try:
        nifty_price_lower = utils.get_spot_price('nse')
        print(f"✓ NIFTY 50 LTP: ₹{nifty_price_lower}")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    # Test invalid exchange
    print("\n=== Testing invalid exchange ===")
    try:
        invalid_price = utils.get_spot_price('INVALID')
        print(f"Unexpected success: {invalid_price}")
    except ValueError as e:
        print(f"✓ Correctly raised ValueError: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
    
    # Test original method still works
    print("\n=== Testing original get_nifty_spot_price() ===")
    try:
        nifty_price_original = utils.get_nifty_spot_price()
        print(f"✓ NIFTY 50 LTP (original method): ₹{nifty_price_original}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    test_get_spot_price()
