"""
Main entry point for the option trading bot.
This module initializes and runs the trading bot with proper configuration.
"""
import sys
from datetime import datetime

from option_trade.config import load_config
from option_trade.trading_bot import TradingBot
from option_trade.logger import TradingLogger


def main():
    """
    Main function to run the trading bot.
    """
    # Initialize logger
    logger = TradingLogger(name="OptionTradingBot")
    
    logger.log_separator()
    logger.info("Option Trading Bot - Starting")
    logger.log_separator()
    
    try:
        # Get access token
        # IMPORTANT: Replace this with your actual Groww API access token
        access_token = input("Enter your Groww API access token: ").strip()
        
        if not access_token:
            logger.error("Access token is required")
            sys.exit(1)
        
        # Load configuration
        logger.info("Loading configuration...")
        config = load_config(access_token)
        
        logger.info(f"Trading Symbol: {config.trading_symbol}")
        logger.info(f"EMA Period: {config.ema_period}")
        logger.info(f"Spread Gap: {config.spread_gap}")
        logger.info(f"Call Spread: {'Enabled' if config.call_spread_enabled else 'Disabled'}")
        logger.info(f"Put Spread: {'Enabled' if config.put_spread_enabled else 'Disabled'}")
        logger.info(f"Trading Start Time: {config.trading_start_time}")
        logger.info(f"Quantity: {config.quantity}")
        
        # Create trading bot
        logger.info("Initializing trading bot...")
        bot = TradingBot(config)
        
        # Run the bot
        logger.info("Starting trading bot...")
        logger.log_separator()
        
        # Run with 60-second check interval
        bot.run(check_interval=60)
        
    except KeyboardInterrupt:
        logger.info("\nBot stopped by user (Ctrl+C)")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.log_separator()
        logger.info("Option Trading Bot - Stopped")
        logger.log_separator()


if __name__ == "__main__":
    main()