import os
import requests
from datetime import datetime, timedelta
from pathlib import Path
import json
import time
import csv


class BhavcopyDownloader:
    """Download bhavcopy files from NSE India"""
    
    def __init__(self, save_dir="/Users/amankumarayush/PycharmProjects/trading_poc/bhavcopy/files",
                 holiday_file="/Users/amankumarayush/PycharmProjects/trading_poc/bhavcopy/holiday.csv"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)
        
        # Load holidays from CSV
        self.holidays = self._load_holidays(holiday_file)
        
        # NSE India requires specific headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/report-detail/eq_security',
            'Connection': 'keep-alive',
        }
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _load_holidays(self, holiday_file):
        """Load holidays from CSV file"""
        holidays = set()
        try:
            with open(holiday_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Parse date in DD-MMM-YYYY format
                    date_str = row['Date'].strip()
                    try:
                        holiday_date = datetime.strptime(date_str, '%d-%b-%Y')
                        holidays.add(holiday_date.date())
                    except ValueError as e:
                        print(f"Warning: Could not parse holiday date '{date_str}': {e}")
            print(f"Loaded {len(holidays)} holidays from {holiday_file}")
        except Exception as e:
            print(f"Warning: Could not load holidays from {holiday_file}: {e}")
        return holidays
    
    def _is_trading_day(self, date_obj):
        """Check if the date is a trading day (not weekend or holiday)"""
        # Check if weekend (Saturday=5, Sunday=6)
        if date_obj.weekday() >= 5:
            return False
        # Check if holiday
        if date_obj.date() in self.holidays:
            return False
        return True
        
    def _get_nse_cookies(self):
        """Get cookies from NSE India homepage"""
        try:
            response = self.session.get('https://www.nseindia.com', timeout=10)
            return response.status_code == 200
        except Exception as e:
            print(f"Error getting NSE cookies: {e}")
            return False
    
    def _format_date(self, date_obj):
        """Format date to NSE format: DD-MMM-YYYY"""
        return date_obj.strftime('%d-%b-%Y')
    
    def _get_filename(self, date_obj):
        """Generate filename for bhavcopy"""
        # Format: bhavcopy_DDMMYYYY.csv or similar
        return f"bhavcopy_{date_obj.strftime('%d%m%Y')}.csv"
    
    def _file_exists(self, filename):
        """Check if file already exists"""
        filepath = self.save_dir / filename
        return filepath.exists()
    
    def _build_url(self, date_str):
        """Build the NSE API URL for bhavcopy download"""
        archives = [
            {
                "name": "Full Bhavcopy and Security Deliverable data",
                "type": "daily-reports",
                "category": "capital-market",
                "section": "equities"
            }
        ]
        
        params = {
            'archives': json.dumps(archives),
            'date': date_str,
            'type': 'equities',
            'mode': 'single'
        }
        
        base_url = 'https://www.nseindia.com/api/reports'
        return base_url, params
    
    def download_file(self, date_obj):
        """Download bhavcopy for a specific date"""
        filename = self._get_filename(date_obj)
        
        # Check if file already exists
        if self._file_exists(filename):
            print(f"✓ File already exists: {filename}")
            return True
        
        date_str = self._format_date(date_obj)
        print(f"Downloading bhavcopy for {date_str}...")
        
        try:
            # Get fresh cookies
            if not self._get_nse_cookies():
                print("Warning: Could not get NSE cookies")
            
            # Small delay to avoid rate limiting
            time.sleep(1)
            
            # Build URL and download
            base_url, params = self._build_url(date_str)
            response = self.session.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                # Check if response has content
                if not response.content:
                    print(f"✗ Empty response for {date_str} (possibly a holiday or non-trading day)")
                    return False
                
                content_type = response.headers.get('Content-Type', '')
                
                # Check if response is CSV (direct file download)
                if 'text/csv' in content_type or 'application/csv' in content_type:
                    # Direct CSV file - save it
                    filepath = self.save_dir / filename
                    filepath.write_bytes(response.content)
                    print(f"✓ Downloaded: {filename}")
                    return True
                else:
                    print(f"✗ Could not parse response for {date_str}")
                    print(f"  Content-Type: {content_type}")
                    print(f"  Error: {e}")
                    return False
            else:
                print(f"✗ Failed to download for {date_str}: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"✗ Error downloading for {date_str}: {e}")
            return False
    
    def download_range(self, from_date, to_date):
        """Download bhavcopy files for a date range"""
        # Parse dates
        if isinstance(from_date, str):
            from_date = datetime.strptime(from_date, '%Y-%m-%d')
        if isinstance(to_date, str):
            to_date = datetime.strptime(to_date, '%Y-%m-%d')
        
        print(f"\nDownloading bhavcopy from {from_date.date()} to {to_date.date()}")
        print(f"Save directory: {self.save_dir}\n")
        
        current_date = from_date
        success_count = 0
        skip_count = 0
        fail_count = 0
        
        while current_date <= to_date:
            # Skip weekends and holidays
            if self._is_trading_day(current_date):
                filename = self._get_filename(current_date)
                
                if self._file_exists(filename):
                    skip_count += 1
                elif self.download_file(current_date):
                    success_count += 1
                else:
                    fail_count += 1
            else:
                # Log skipped non-trading days
                if current_date.weekday() >= 5:
                    print(f"⊘ Skipping weekend: {current_date.date()}")
                else:
                    print(f"⊘ Skipping holiday: {current_date.date()}")
            
            current_date += timedelta(days=1)
        
        print(f"\n{'='*50}")
        print(f"Download Summary:")
        print(f"  Successfully downloaded: {success_count}")
        print(f"  Already existed: {skip_count}")
        print(f"  Failed: {fail_count}")
        print(f"{'='*50}\n")


def main():
    """Main function to run the downloader"""
    # Example usage
    downloader = BhavcopyDownloader()
    
    # Get date range from user or use defaults
    print("NSE Bhavcopy Downloader")
    print("="*50)
    
    from_date_str = input("Enter from date (YYYY-MM-DD) [default: 2025-12-15]: ").strip()
    to_date_str = input("Enter to date (YYYY-MM-DD) [default: 2025-12-26]: ").strip()
    
    # Use defaults if not provided
    from_date = from_date_str if from_date_str else "2025-12-15"
    to_date = to_date_str if to_date_str else "2025-12-26"
    
    # Download files
    downloader.download_range(from_date, to_date)


if __name__ == "__main__":
    main()