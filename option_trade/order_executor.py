"""
Order execution module.
Follows Single Responsibility Principle - only handles order placement.
"""
from typing import Optional, Dict
from growwapi import GrowwAPI


class OrderExecutor:
    """
    Responsible for executing orders via Groww API.
    Implements Single Responsibility Principle.
    """
    
    def __init__(self, groww_api: GrowwAPI, expiry: str, spread_gap: int = 200):
        """
        Initialize order executor.
        
        Args:
            groww_api: Authenticated GrowwAPI instance
            expiry: Option expiry (e.g., "25N04")
            spread_gap: Gap between strike prices for spread
        """
        self.groww = groww_api
        self.expiry = expiry
        self.spread_gap = spread_gap
    
    def get_atm_strike(self, spot_price: float) -> int:
        """
        Get At-The-Money strike price.
        
        Args:
            spot_price: Current spot price
            
        Returns:
            ATM strike price (rounded to nearest 50)
        """
        return round(float(spot_price) / 50) * 50
    
    def place_call_spread(self, strike_price: int, quantity: int) -> Dict:
        """
        Place call spread order (buy higher strike, sell lower strike).
        
        Args:
            strike_price: Base strike price
            quantity: Quantity to trade
            
        Returns:
            Dictionary with order responses
        """
        try:
            # Buy higher strike (OTM)
            buy_response = self.groww.place_order(
                trading_symbol=f"NIFTY{self.expiry}{strike_price + self.spread_gap}CE",
                quantity=quantity,
                validity=self.groww.VALIDITY_DAY,
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_FNO,
                product=self.groww.PRODUCT_MIS,
                order_type=self.groww.ORDER_TYPE_MARKET,
                transaction_type=self.groww.TRANSACTION_TYPE_BUY,
            )
            
            # Sell lower strike (ATM)
            sell_response = self.groww.place_order(
                trading_symbol=f"NIFTY{self.expiry}{strike_price}CE",
                quantity=quantity,
                validity=self.groww.VALIDITY_DAY,
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_FNO,
                product=self.groww.PRODUCT_MIS,
                order_type=self.groww.ORDER_TYPE_MARKET,
                transaction_type=self.groww.TRANSACTION_TYPE_SELL,
            )
            
            return {
                'status': 'success',
                'type': 'CALL_SPREAD',
                'buy_order': buy_response,
                'sell_order': sell_response,
                'strike': strike_price,
                'quantity': quantity
            }
        except Exception as e:
            return {
                'status': 'error',
                'type': 'CALL_SPREAD',
                'error': str(e)
            }
    
    def place_put_spread(self, strike_price: int, quantity: int) -> Dict:
        """
        Place put spread order (buy lower strike, sell higher strike).
        
        Args:
            strike_price: Base strike price
            quantity: Quantity to trade
            
        Returns:
            Dictionary with order responses
        """
        try:
            # Buy lower strike (OTM)
            buy_response = self.groww.place_order(
                trading_symbol=f"NIFTY{self.expiry}{strike_price - self.spread_gap}PE",
                quantity=quantity,
                validity=self.groww.VALIDITY_DAY,
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_FNO,
                product=self.groww.PRODUCT_MIS,
                order_type=self.groww.ORDER_TYPE_MARKET,
                transaction_type=self.groww.TRANSACTION_TYPE_BUY,
            )
            
            # Sell higher strike (ATM)
            sell_response = self.groww.place_order(
                trading_symbol=f"NIFTY{self.expiry}{strike_price}PE",
                quantity=quantity,
                validity=self.groww.VALIDITY_DAY,
                exchange=self.groww.EXCHANGE_NSE,
                segment=self.groww.SEGMENT_FNO,
                product=self.groww.PRODUCT_MIS,
                order_type=self.groww.ORDER_TYPE_MARKET,
                transaction_type=self.groww.TRANSACTION_TYPE_SELL,
            )
            
            return {
                'status': 'success',
                'type': 'PUT_SPREAD',
                'buy_order': buy_response,
                'sell_order': sell_response,
                'strike': strike_price,
                'quantity': quantity
            }
        except Exception as e:
            return {
                'status': 'error',
                'type': 'PUT_SPREAD',
                'error': str(e)
            }
    
    def close_all_positions(self) -> Dict:
        """
        Close all open FNO positions.
        
        Returns:
            Dictionary with closure summary
        """
        try:
            positions_response = self.groww.get_positions()
            
            if not positions_response or 'positions' not in positions_response:
                return {
                    'status': 'error',
                    'message': 'Unable to fetch positions'
                }
            
            positions = positions_response['positions']
            fno_positions = [pos for pos in positions if pos.get('segment') == self.groww.SEGMENT_FNO]
            
            if not fno_positions:
                return {
                    'status': 'success',
                    'message': 'No FNO positions to close',
                    'closed_count': 0
                }
            
            closed_positions = []
            failed_positions = []
            
            for position in fno_positions:
                try:
                    trading_symbol = position.get('trading_symbol')
                    net_quantity = position.get('net_quantity', 0)
                    
                    if net_quantity == 0:
                        continue
                    
                    # Determine transaction type (reverse of current position)
                    if net_quantity > 0:
                        transaction_type = self.groww.TRANSACTION_TYPE_SELL
                        quantity = abs(net_quantity)
                    else:
                        transaction_type = self.groww.TRANSACTION_TYPE_BUY
                        quantity = abs(net_quantity)
                    
                    close_order_response = self.groww.place_order(
                        trading_symbol=trading_symbol,
                        quantity=quantity,
                        validity=self.groww.VALIDITY_DAY,
                        exchange=self.groww.EXCHANGE_NSE,
                        segment=self.groww.SEGMENT_FNO,
                        product=position.get('product', self.groww.PRODUCT_MIS),
                        order_type=self.groww.ORDER_TYPE_MARKET,
                        transaction_type=transaction_type,
                    )
                    
                    closed_positions.append({
                        'symbol': trading_symbol,
                        'quantity': quantity,
                        'response': close_order_response
                    })
                except Exception as e:
                    failed_positions.append({
                        'symbol': trading_symbol,
                        'error': str(e)
                    })
            
            return {
                'status': 'success',
                'total_positions': len(fno_positions),
                'closed_count': len(closed_positions),
                'failed_count': len(failed_positions),
                'closed_positions': closed_positions,
                'failed_positions': failed_positions
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error closing positions: {str(e)}'
            }