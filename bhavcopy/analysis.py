import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
import csv


class BhavcopyAnalyzer:
    """Analyze bhavcopy data for specific symbols"""
    
    def __init__(self, data_dir="/Users/amankumarayush/PycharmProjects/trading_poc/bhavcopy/files",
                 holiday_file="/Users/amankumarayush/PycharmProjects/trading_poc/bhavcopy/holiday.csv"):
        self.data_dir = Path(data_dir)
        self.holidays = self._load_holidays(holiday_file)
    
    def _load_holidays(self, holiday_file):
        """Load holidays from CSV file"""
        holidays = set()
        try:
            with open(holiday_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date_str = row['Date'].strip()
                    try:
                        holiday_date = datetime.strptime(date_str, '%d-%b-%Y')
                        holidays.add(holiday_date.date())
                    except ValueError:
                        pass
        except Exception as e:
            print(f"Warning: Could not load holidays: {e}")
        return holidays
    
    def _is_trading_day(self, date_obj):
        """Check if the date is a trading day"""
        if date_obj.weekday() >= 5:  # Weekend
            return False
        if date_obj.date() in self.holidays:  # Holiday
            return False
        return True
    
    def _get_last_n_trading_days(self, n, end_date=None):
        """Get the last N trading days from end_date (default: today)"""
        if end_date is None:
            end_date = datetime.now()
        elif isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        trading_days = []
        current_date = end_date
        
        # Go back up to 2*n days to find n trading days
        for _ in range(n * 3):  # Safety margin
            if self._is_trading_day(current_date):
                trading_days.append(current_date)
                if len(trading_days) == n:
                    break
            current_date -= timedelta(days=1)
        
        return sorted(trading_days)  # Return in chronological order
    
    def _get_bhavcopy_filename(self, date_obj):
        """Generate bhavcopy filename for a date"""
        return f"bhavcopy_{date_obj.strftime('%d%m%Y')}.csv"
    
    def _read_bhavcopy(self, date_obj):
        """Read a single bhavcopy file"""
        filename = self._get_bhavcopy_filename(date_obj)
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            print(f"Warning: File not found: {filename}")
            return None
        
        try:
            # Read CSV with proper handling of spaces in column names
            df = pd.read_csv(filepath, skipinitialspace=True)
            # Strip whitespace from column names
            df.columns = df.columns.str.strip()
            return df
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return None
    
    def get_symbol_data(self, symbol, n_days, end_date=None):
        """
        Get trading data for a symbol over the last N trading days
        
        Parameters:
        -----------
        symbol : str
            Stock symbol (e.g., 'RELIANCE', 'TCS')
        n_days : int
            Number of trading days to retrieve
        end_date : str or datetime, optional
            End date (default: today). Format: 'YYYY-MM-DD'
        
        Returns:
        --------
        pandas.DataFrame
            DataFrame with columns: DATE, SYMBOL, TTL_TRD_QNTY, NO_OF_TRADES, DELIV_QTY, DELIV_PER
        """
        # Get last N trading days
        trading_days = self._get_last_n_trading_days(n_days, end_date)
        
        if not trading_days:
            print(f"No trading days found")
            return pd.DataFrame()
        
        print(f"\nAnalyzing {symbol} for last {n_days} trading days:")
        print(f"Date range: {trading_days[0].date()} to {trading_days[-1].date()}\n")
        
        # Collect data from all trading days
        all_data = []
        
        for date_obj in trading_days:
            df = self._read_bhavcopy(date_obj)
            
            if df is None:
                continue
            
            # Filter for the specific symbol
            symbol_data = df[df['SYMBOL'] == symbol.upper()]
            
            if not symbol_data.empty:
                # Extract required columns
                for _, row in symbol_data.iterrows():
                    all_data.append({
                        'DATE': date_obj.strftime('%d-%b-%Y'),
                        'SYMBOL': row['SYMBOL'],
                        'SERIES': row.get('SERIES', 'N/A'),
                        'CLOSE_PRICE': row.get('CLOSE_PRICE', 0),
                        'TTL_TRD_QNTY': row.get('TTL_TRD_QNTY', 0),
                        'NO_OF_TRADES': row.get('NO_OF_TRADES', 0),
                        'DELIV_QTY': row.get('DELIV_QTY', 0),
                        'DELIV_PER': row.get('DELIV_PER', 0)
                    })
        
        if not all_data:
            print(f"No data found for symbol: {symbol}")
            return pd.DataFrame()
        
        # Create DataFrame
        result_df = pd.DataFrame(all_data)
        
        # Convert numeric columns
        numeric_cols = ['CLOSE_PRICE', 'TTL_TRD_QNTY', 'NO_OF_TRADES', 'DELIV_QTY', 'DELIV_PER']
        for col in numeric_cols:
            result_df[col] = pd.to_numeric(result_df[col], errors='coerce')
        
        return result_df
    
    def print_summary(self, df):
        """Print a summary of the data"""
        if df.empty:
            print("No data to display")
            return
        
        print("\n" + "="*80)
        print(f"Summary for {df['SYMBOL'].iloc[0]}")
        print("="*80)
        print(df.to_string(index=False))
        print("\n" + "-"*80)
        print("Statistics:")
        print("-"*80)
        print(f"Total Trading Days: {len(df)}")
        print(f"Average Daily Volume: {df['TTL_TRD_QNTY'].mean():,.0f}")
        print(f"Average Daily Trades: {df['NO_OF_TRADES'].mean():,.0f}")
        print(f"Average Delivery Qty: {df['DELIV_QTY'].mean():,.0f}")
        print(f"Average Delivery %: {df['DELIV_PER'].mean():.2f}%")
        print(f"Total Volume: {df['TTL_TRD_QNTY'].sum():,.0f}")
        print(f"Total Trades: {df['NO_OF_TRADES'].sum():,.0f}")
        print("="*80 + "\n")


def main():
    """Example usage"""
    analyzer = BhavcopyAnalyzer()
    
    # Get user input
    print("Bhavcopy Data Analyzer")
    print("="*50)
    
    symbol = input("Enter stock symbol (e.g., RELIANCE, TCS): ").strip().upper()
    n_days_str = input("Enter number of trading days (default: 5): ").strip()
    n_days = int(n_days_str) if n_days_str else 5
    
    # Get data
    df = analyzer.get_symbol_data(symbol, n_days)
    
    # Print summary
    analyzer.print_summary(df)
    
    # Optionally save to CSV
    save = input("Save to CSV? (y/n): ").strip().lower()
    if save == 'y':
        output_file = f"{symbol}_last_{n_days}_days.csv"
        df.to_csv(output_file, index=False)
        print(f"\n✓ Data saved to: {output_file}")


if __name__ == "__main__":
    main()