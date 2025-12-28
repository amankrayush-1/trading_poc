import pandas as pd
from playwright.sync_api import sync_playwright
import time
import os

symbols = pd.read_csv("nse_symbols.csv")["symbol"].tolist()

BASE_URL = "https://www.tradingview.com/chart/?symbol=NSE:{}"
SAVE_DIR = "screenshots"

os.makedirs(SAVE_DIR, exist_ok=True)

def take_screenshot(symbol, timeframe, page):
    # Change timeframe using TradingView hotkeys
    if timeframe == "D":
        page.keyboard.press(",")
        time.sleep(0.5)
        page.keyboard.press("d")  # Use lowercase
        page.keyboard.press("Enter")  # Press Return (Mac)
    elif timeframe == "W":
        page.keyboard.press(",")
        time.sleep(0.5)
        page.keyboard.press("w")  # Use lowercase
        page.keyboard.press("Enter")  # Press Return (Mac)
    elif timeframe == "M":
        page.keyboard.press(",")
        time.sleep(0.5)
        page.keyboard.press("m")  # Use lowercase
        page.keyboard.press("Enter")  # Press Return (Mac)

    time.sleep(3)

    filename = f"{SAVE_DIR}/{symbol}_{timeframe}.png"
    page.screenshot(path=filename, full_page=False)
    print(f"Saved {filename}")

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=False,
        args=['--start-maximized']
    )
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        no_viewport=True  # This allows the page to use the full window size
    )
    page = context.new_page()

    for symbol in symbols:
        url = BASE_URL.format(symbol)
        page.goto(url)
        page.wait_for_timeout(5000)

        # take_screenshot(symbol, "D", page)
        # take_screenshot(symbol, "W", page)
        take_screenshot(symbol, "M", page)

    browser.close()
