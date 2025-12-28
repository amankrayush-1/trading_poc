"""
Example usage of BhavcopyDownloader

This script demonstrates how to use the BhavcopyDownloader class
to download bhavcopy files from NSE India.
"""

from download_file import BhavcopyDownloader
from datetime import datetime, timedelta


def example_1_download_single_date():
    """Example: Download bhavcopy for a single date"""
    print("\n" + "="*60)
    print("Example 1: Download for a single date")
    print("="*60)
    
    downloader = BhavcopyDownloader()
    date = datetime(2025, 12, 26)
    downloader.download_file(date)


def example_2_download_date_range():
    """Example: Download bhavcopy for a date range"""
    print("\n" + "="*60)
    print("Example 2: Download for a date range")
    print("="*60)
    
    downloader = BhavcopyDownloader()
    from_date = "2025-12-20"
    to_date = "2025-12-26"
    downloader.download_range(from_date, to_date)


def example_3_download_last_week():
    """Example: Download bhavcopy for the last week"""
    print("\n" + "="*60)
    print("Example 3: Download for the last week")
    print("="*60)
    
    downloader = BhavcopyDownloader()
    to_date = datetime.now()
    from_date = to_date - timedelta(days=7)
    downloader.download_range(from_date, to_date)


def example_4_custom_directory():
    """Example: Download to a custom directory"""
    print("\n" + "="*60)
    print("Example 4: Download to custom directory")
    print("="*60)
    
    custom_dir = "/Users/amankumarayush/PycharmProjects/trading_poc/bhavcopy/custom_files"
    downloader = BhavcopyDownloader(save_dir=custom_dir)
    downloader.download_range("2025-12-23", "2025-12-26")


if __name__ == "__main__":
    # Run the example you want to test
    # Uncomment the example you want to run:
    
    # example_1_download_single_date()
    example_2_download_date_range()
    # example_3_download_last_week()
    # example_4_custom_directory()