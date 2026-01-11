# 15-Minute OHLC Data Filler

This script reads an Excel file with 2 sheets (2025 and 2024), extracts dates from Column B, and fills the "First 15 Min" OHLC data in columns H-K using the Groww API.

## Excel File Structure

The Excel file has the following structure:

### Sheets
- **Sheet 1**: "2025" (contains 2025 data)
- **Sheet 2**: "2024" (contains 2024 data)

### Columns
| Column | Header | Description | Status |
|--------|--------|-------------|--------|
| A | Index Name | Name of the index (e.g., "NIFTY 50") | Already filled |
| B | Date | Trading date | Already filled |
| C | Open | Daily Open price | Already filled |
| D | High | Daily High price | Already filled |
| E | Low | Daily Low price | Already filled |
| F | Close | Daily Close price | Already filled |
| G | - | Empty column | - |
| H | First 15 Min - Open | 15-min Open price | **To be filled** |
| I | First 15 Min - High | 15-min High price | **To be filled** |
| J | First 15 Min - Low | 15-min Low price | **To be filled** |
| K | First 15 Min - Close | 15-min Close price | **To be filled** |

## Prerequisites

1. **Python 3.7+** installed on your system
2. **Virtual environment** (`.venv` folder in project)
3. **Groww API credentials** (TOTP token and secret)
4. **Excel file** at `/Users/amankumarayush/Downloads/OHLC.xlsx`

## Installation

### Activate Virtual Environment and Install Dependencies

```bash
# Navigate to project directory
cd /Users/amankumarayush/PycharmProjects/trading_poc

# Activate virtual environment
cd .venv
source bin/activate
cd ..

# Install required packages
pip install openpyxl pandas growwapi pyotp
```

## Configuration

Before running the script, update your Groww API credentials in [`fill_ohlc_data.py`](fill_ohlc_data.py:16-17):

```python
# Replace these with your actual credentials
API_KEY = "YOUR_TOTP_TOKEN"
TOTP_SECRET = "YOUR_TOTP_SECRET"
```

### How to get Groww API credentials:

1. Go to [Groww API Keys Page](https://groww.in/trade-api/api-keys)
2. Log in to your Groww account
3. Click on 'Generate TOTP token'
4. Copy the TOTP token and secret
5. Update the script with your credentials

## Usage

### Step 1: Activate Virtual Environment
```bash
cd .venv
source bin/activate
cd ..
```

### Step 2: Run the Script
```bash
python3 fill_ohlc_data.py
```

### Complete Command (One-liner)
```bash
cd .venv && source bin/activate && cd .. && python3 fill_ohlc_data.py
```

## What the Script Does

1. ✅ Reads Excel file from `/Users/amankumarayush/Downloads/OHLC.xlsx`
2. ✅ Processes both sheets: "2025" and "2024"
3. ✅ For each row:
   - Reads the date from **Column B**
   - Checks if 15-min OHLC is already filled (Column H)
   - If empty, fetches 15-minute OHLC data from Groww API
   - Fills columns **H, I, J, K** with Open, High, Low, Close
4. ✅ Saves results to `/Users/amankumarayush/Downloads/OHLC_filled.xlsx`
5. ✅ Provides detailed progress and summary for each sheet

## Output

The script creates a new file: `/Users/amankumarayush/Downloads/OHLC_filled.xlsx`

### Before (Columns H-K empty):
| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| NIFTY 50 | 2025-01-01 | 23637.65 | 23822.8 | 23562.8 | 23742.9 | - | - | - | - | - |

### After (Columns H-K filled):
| A | B | C | D | E | F | G | H | I | J | K |
|---|---|---|---|---|---|---|---|---|---|---|
| NIFTY 50 | 2025-01-01 | 23637.65 | 23822.8 | 23562.8 | 23742.9 | - | 23640.5 | 23680.0 | 23620.0 | 23665.5 |

## Features

- ✅ Processes multiple sheets (2025 and 2024)
- ✅ Reads dates from Column B
- ✅ Fills First 15 Min OHLC in columns H-K
- ✅ Skips rows that already have 15-min data
- ✅ Handles missing or invalid dates gracefully
- ✅ Rate limiting (500ms delay) to respect API limits
- ✅ Detailed progress logging for each row
- ✅ Summary statistics for each sheet
- ✅ Preserves original file (saves to new file)

## Example Run

```bash
$ cd .venv && source bin/activate && cd .. && python3 fill_ohlc_data.py

================================================================================
15-Minute OHLC Data Filler
Fills First 15 Min OHLC data in columns H-K
================================================================================
Reading Excel file: /Users/amankumarayush/Downloads/OHLC.xlsx
✓ Excel file loaded successfully
Sheets found: ['2025', '2024']
✓ Successfully authenticated with Groww API

================================================================================
Processing Sheet: 2025
================================================================================
Total data rows: 222
Row 3: Fetching 15-min OHLC for 2025-01-01... ✓ O=23640.50, H=23680.00, L=23620.00, C=23665.50
Row 4: Fetching 15-min OHLC for 2025-01-02... ✓ O=23785.00, H=23820.00, L=23770.00, C=23800.00
...

--- Sheet '2025' Summary ---
Total rows processed: 222
Successfully filled: 220
Skipped (already filled or invalid): 2
Errors: 0

================================================================================
Processing Sheet: 2024
================================================================================
Total data rows: 249
Row 3: Fetching 15-min OHLC for 2024-01-01... ✓ O=21730.00, H=21750.00, L=21710.00, C=21735.00
...

--- Sheet '2024' Summary ---
Total rows processed: 249
Successfully filled: 248
Skipped (already filled or invalid): 1
Errors: 0

================================================================================
Saving results to: /Users/amankumarayush/Downloads/OHLC_filled.xlsx
✓ Successfully saved filled OHLC data

================================================================================
Process completed!
================================================================================
```

## Customization

### Change Trading Symbol
By default, the script fetches data for `NSE_NIFTY`. To change this, modify line 135 in [`fill_ohlc_data.py`](fill_ohlc_data.py:135):

```python
trading_symbol = "NSE_NIFTY"  # Change to your desired symbol
# Examples: "NSE_BANKNIFTY", "NSE_RELIANCE", etc.
```

### Change File Paths
Update the file paths at the top of the script:

```python
EXCEL_FILE_PATH = '/Users/amankumarayush/Downloads/OHLC.xlsx'
OUTPUT_FILE_PATH = '/Users/amankumarayush/Downloads/OHLC_filled.xlsx'
```

### Adjust Rate Limiting
Modify the sleep duration on line 152:

```python
time.sleep(0.5)  # Change to adjust delay between API calls
```

## Troubleshooting

### Error: "ModuleNotFoundError: No module named 'openpyxl'"
**Solution**: Make sure virtual environment is activated and packages are installed:
```bash
cd .venv && source bin/activate && cd .. && pip install openpyxl pandas
```

### Error: "File not found"
**Solution**: Ensure the Excel file exists at `/Users/amankumarayush/Downloads/OHLC.xlsx`

### Error: "Failed to authenticate with Groww API"
**Solution**: 
1. Check your API credentials are correct in the script
2. Ensure your TOTP secret is valid
3. Try generating a new TOTP token

### Script skips all rows
**Solution**: Check if columns H-K already have data. The script skips rows that are already filled.

## Rate Limits

According to Groww API documentation:
- **Live Data APIs** (including OHLC): 10 requests/second, 300 requests/minute

The script includes a 500ms delay between requests to stay within limits.

## Important Notes

1. **Preserves Original**: The script saves to a new file, keeping your original intact
2. **Smart Skip**: Automatically skips rows that already have 15-min data
3. **Both Sheets**: Processes both 2025 and 2024 sheets automatically
4. **Date from Column B**: Always reads dates from Column B as specified
5. **Fills H-K**: Only fills the First 15 Min OHLC columns (H, I, J, K)

## Support

For issues related to:
- **Groww API**: Visit [Groww API Documentation](https://groww.in/trade-api/docs/python-sdk)
- **Script issues**: Check the error messages and logs

## Files in Project

- [`fill_ohlc_data.py`](fill_ohlc_data.py) - Main script to fill OHLC data
- [`inspect_excel.py`](inspect_excel.py) - Utility to inspect Excel file structure
- [`requirements.txt`](../requirements.txt) - Python dependencies
- [`OHLC_FILLER_README.md`](OHLC_FILLER_README.md) - This documentation

## License

This script is provided as-is for educational and personal use.