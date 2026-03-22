# Running Angel One Integration Test

## Quick Start

### Option 1: Using Config File (Recommended)

**PowerShell:**
```powershell
cd StockNotificationManager

# Copy example config
copy config\angel_config.example.json config\angel_config.json

# Edit config/angel_config.json with your credentials
notepad config\angel_config.json

# Activate venv
.\.venv\Scripts\activate.bat

# Run test
python test_broker.py
```

**config/angel_config.json format:**
```json
{
  "api_key": "your_api_key_here",
  "client_id": "your_client_id_here",
  "password": "your_password_here",
  "totp_secret": "your_totp_secret (optional)"
}
```

### Option 2: Using main.py with --test flag

```powershell
# Ensure config/angel_config.json is created (see Option 1)

# Activate venv
.\.venv\Scripts\activate.bat

# Run in test mode
python main.py --test
```

### Option 3: Run normally with GUI and background test

Edit `main.py` and uncomment these lines:
```python
# Uncomment these lines in the main() function:
test_thread = threading.Thread(target=test_angel_one_integration, daemon=True)
test_thread.start()
logger.info("Angel One integration test started in background thread")
```

Then run normally:
```powershell
python main.py
```

## Expected Output

When credentials are configured:
```
=== Starting Angel One Integration Test ===
Broker manager created
Attempting to authenticate with Angel One...
✓ Successfully authenticated with Angel One
Active broker: Angel One
Status: connected

=== Fetching Nifty 50 Scripts from NSE ===
✓ Found: RELIANCE - Reliance Industries Ltd
✓ Found: TCS - Tata Consultancy Services Ltd
✓ Found: HDFCBANK - HDFC Bank Ltd
...

=== Summary ===
Total scripts fetched: 10
Symbol          Token      Name                                     Lot Size
--------------------------------------------------------------------------------
RELIANCE        2885       Reliance Industries Ltd                  1
TCS             11536      Tata Consultancy Services Ltd            1
...

=== Getting Last Traded Prices ===
RELIANCE        LTP: ₹  2,456.75  Change:  +1.23%  Volume:   1,234,567
TCS             LTP: ₹  3,789.50  Change:  -0.45%  Volume:     987,654
...

=== Disconnecting ===
✓ Disconnected from Angel One
=== Test Completed ===
```

When credentials are NOT configured:
```
=== Starting Angel One Integration Test ===
Broker manager created
Angel One credentials not configured!
Set environment variables: ANGEL_API_KEY, ANGEL_CLIENT_ID, ANGEL_PASSWORD
Skipping broker authentication test
Created broker: Angel One
Note: Broker is not authenticated. Real API calls will fail.
```

## Features Tested

1. ✅ Broker Manager creation
2. ✅ Angel One authentication
3. ✅ Search for NSE scripts
4. ✅ Fetch Nifty 50 stock list
5. ✅ Get Last Traded Price (LTP)
6. ✅ Display stock information
7. ✅ Proper disconnect and cleanup

## Nifty 50 Stocks Included

The test fetches the first 10 stocks from the Nifty 50 index:
- RELIANCE, TCS, HDFCBANK, INFY, HINDUNILVR
- ICICIBANK, KOTAKBANK, SBIN, BHARTIARTL, BAJFINANCE

Full list of 50 stocks is defined in `main.py` under `NIFTY_50_SYMBOLS`.

## Troubleshooting

### Error: "SmartApi not installed"
```powershell
pip install smartapi-python
pip freeze > requirements.txt
```

### Error: "Authentication failed"
- Verify your API credentials
- Ensure API access is enabled in Angel One account
- Check if TOTP is required and provide it
- See `Documentation/AngelOne_SmartAPI_Setup.md` for detailed setup

### Error: "Import 'SmartApi' could not be resolved"
This is a linting error and can be ignored if the library is installed in your venv.

## Notes

- The test runs in a separate thread when integrated with GUI
- Credentials are NEVER logged or displayed
- Always use environment variables or secure config for production
- The test gracefully handles missing credentials
- Broker connection is properly cleaned up on exit
