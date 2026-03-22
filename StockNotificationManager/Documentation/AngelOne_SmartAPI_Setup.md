# Angel One SmartAPI Integration Guide

## Overview
This guide explains how to set up and use Angel One SmartAPI with the Stock Notification Manager application.

---

## Prerequisites

1. **Angel One Trading Account**
   - Active Angel One (Angel Broking) trading and demat account
   - Account must be KYC verified and active

2. **Python Environment**
   - Python 3.8 or higher
   - Virtual environment set up (see main README)

---

## Step 1: Register for SmartAPI Access

### 1.1 Create SmartAPI Account

1. Visit the Angel One SmartAPI portal: [https://smartapi.angelbroking.com/](https://smartapi.angelbroking.com/)
2. Click on **"Get Started"** or **"Sign Up"**
3. Log in using your Angel One credentials:
   - Client ID (your trading account ID)
   - Password
   - MPIN

### 1.2 Create API App

1. After logging in, navigate to **"My Apps"** section
2. Click **"Create New App"**
3. Fill in the application details:
   - **App Name**: Stock Notification Manager (or any name you prefer)
   - **Description**: Personal stock monitoring application
   - **App Type**: Select "Personal Use"
   - **Redirect URL**: http://localhost (for personal use)
4. Click **"Create App"**

### 1.3 Get API Credentials

Once your app is created, you'll receive:

- **API Key**: A unique key for your application (e.g., `ABC123xyz`)
- **Client ID**: Your Angel One trading account ID (e.g., `A12345`)
- **Client Secret**: Keep this secure (optional for some operations)

**Important**: Save these credentials securely. Never share them publicly.

---

## Step 2: Enable API Trading

### 2.1 Activate API Trading in Angel One Account

1. Log in to your Angel One account at [https://www.angelone.in/](https://www.angelone.in/)
2. Go to **Profile** → **Settings**
3. Navigate to **"API Settings"** or **"Third-Party Apps"**
4. Enable **"Allow API Trading"**
5. You may need to complete additional verification:
   - OTP verification via registered mobile
   - Email verification
   - MPIN confirmation

### 2.2 Set Trading Permissions

Configure what operations the API can perform:
- ✅ **Market Data Access**: Enable for LTP, quotes, and market data
- ✅ **Order Placement**: Enable if you want to place orders (optional)
- ✅ **Portfolio Access**: Enable to view holdings and positions
- ⚠️ **Fund Transfer**: Keep disabled for security

---

## Step 3: Install Required Libraries

### 3.1 Activate Virtual Environment

```powershell
cd StockNotificationManager
.\.venv\Scripts\activate.bat
```

### 3.2 Install SmartAPI Python Library

```powershell
pip install smartapi-python
```

### 3.3 Verify Installation

```powershell
python -c "from SmartApi import SmartConnect; print('SmartAPI installed successfully')"
```

### 3.4 Update Requirements

```powershell
pip freeze > requirements.txt
```

---

## Step 4: Configure Application

### 4.1 Create Configuration File (Optional)

Create a file `config/angel_one_config.json` (add to .gitignore):

```json
{
  "api_key": "your_api_key_here",
  "client_id": "your_client_id_here",
  "password": "your_password_here",
  "totp_secret": "optional_totp_secret"
}
```

**Security Note**: Never commit credentials to version control. Use environment variables or secure configuration management.

### 4.2 Environment Variables (Recommended)

Set environment variables in PowerShell:

```powershell
$env:ANGEL_API_KEY="your_api_key_here"
$env:ANGEL_CLIENT_ID="your_client_id_here"
$env:ANGEL_PASSWORD="your_password_here"
```

---

## Step 5: Authentication Process

### 5.1 Two-Factor Authentication (2FA)

Angel One requires 2FA for API access. You have two options:

#### Option A: TOTP (Time-based One-Time Password)

1. Enable TOTP in your Angel One account settings
2. Use an authenticator app (Google Authenticator, Authy, etc.)
3. Get the TOTP secret key from Angel One
4. Pass the current TOTP code during authentication

#### Option B: Manual OTP

1. During login, an OTP will be sent to your registered mobile
2. Enter the OTP within the validity period (typically 3 minutes)

### 5.2 Authentication Code Example

```python
from src.broker_manager import BrokerManager, BrokerType
import pyotp  # For TOTP generation

# Initialize broker manager
manager = BrokerManager()

# Generate TOTP (if using TOTP)
totp_secret = "YOUR_TOTP_SECRET"
totp = pyotp.TOTP(totp_secret).now()

# Authenticate
credentials = {
    'api_key': 'your_api_key',
    'client_id': 'your_client_id',
    'password': 'your_password',
    'totp': totp  # Optional if using manual OTP
}

success = manager.set_active_broker(BrokerType.ANGEL_ONE, credentials)

if success:
    print("Successfully connected to Angel One!")
    broker = manager.active_broker
else:
    print("Authentication failed!")
```

---

## Step 6: Using the API

### 6.1 Search for Scripts

```python
# Search for a stock
results = broker.search_scripts("RELIANCE", "NSE")
for script in results:
    print(f"{script.symbol} - {script.name}")
```

### 6.2 Get Last Traded Price (LTP)

```python
# Get LTP for a single script
ltp_data = broker.get_ltp("RELIANCE", "NSE")
if ltp_data:
    print(f"LTP: ₹{ltp_data.ltp}")
    print(f"Change: {ltp_data.change_percent}%")
```

### 6.3 Monitor Active Scripts

```python
# Add scripts to monitoring list
broker.add_active_script("RELIANCE", "NSE")
broker.add_active_script("TCS", "NSE")
broker.add_active_script("INFY", "NSE")

# Get all active scripts
active = broker.active_scripts
print(f"Monitoring {len(active)} scripts")
```

### 6.4 Subscribe to Live Data

```python
def on_market_data(data):
    """Callback for real-time market data"""
    print(f"Live data: {data}")

# Subscribe to live feed
broker.subscribe_live_data(on_market_data)

# Unsubscribe when done
broker.unsubscribe_live_data()
```

---

## Step 7: Rate Limits and Best Practices

### 7.1 API Rate Limits

Angel One SmartAPI has rate limits:
- **Market Data**: 1 request per second
- **Order Placement**: 10 orders per second
- **Bulk Requests**: Max 50 instruments per request

### 7.2 Best Practices

1. **Cache Data**: Don't fetch the same data repeatedly
2. **Batch Requests**: Use bulk APIs when possible
3. **Handle Errors**: Implement retry logic with exponential backoff
4. **Session Management**: Refresh tokens before expiry
5. **Disconnect Properly**: Always call `disconnect()` when done

### 7.3 Session Validity

- Access tokens are valid for **24 hours**
- Refresh tokens before expiry
- Implement automatic token refresh in production

---

## Troubleshooting

### Common Issues

#### 1. Authentication Failed
- **Cause**: Incorrect credentials or expired TOTP
- **Solution**: Verify API key, client ID, and password. Generate fresh TOTP.

#### 2. Session Expired
- **Cause**: Token validity exceeded
- **Solution**: Re-authenticate to get a new session token.

#### 3. Rate Limit Exceeded
- **Cause**: Too many requests in short time
- **Solution**: Implement rate limiting and request throttling.

#### 4. WebSocket Connection Failed
- **Cause**: Network issues or invalid feed token
- **Solution**: Check internet connectivity and re-authenticate.

#### 5. Script Not Found
- **Cause**: Invalid symbol or exchange
- **Solution**: Use `search_scripts()` to find correct symbol format.

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## Security Considerations

### ⚠️ Important Security Guidelines

1. **Never Hardcode Credentials**: Use environment variables or secure vaults
2. **Add to .gitignore**: Ensure config files with credentials are not committed
3. **Use HTTPS**: Always use secure connections
4. **Rotate Keys**: Regularly rotate API keys (every 3-6 months)
5. **Monitor Usage**: Check Angel One portal for unauthorized API access
6. **Limit Permissions**: Enable only required API permissions
7. **Secure Storage**: Use encryption for stored credentials

### Example .gitignore Entries

```
# Angel One Credentials
config/angel_one_config.json
.env
*.secret

# Logs may contain sensitive data
logs/*.log
```

---

## Support and Resources

### Official Resources
- **SmartAPI Documentation**: [https://smartapi.angelbroking.com/docs](https://smartapi.angelbroking.com/docs)
- **API Support**: apisupport@angelbroking.com
- **Trading Support**: support@angelone.in

### Community
- **GitHub Issues**: Report bugs in the repository
- **Developer Forum**: Angel One developer community
- **Stack Overflow**: Tag questions with `angel-one` and `smartapi`

---

## API Pricing

Angel One SmartAPI is typically **free** for personal use with an active trading account. However:
- Market data charges may apply based on your subscription
- Check with Angel One for current pricing
- Trading charges apply as per your brokerage plan

---

## Compliance and Legal

- API usage is subject to Angel One's Terms of Service
- Follow SEBI guidelines for algorithmic trading
- Maintain audit logs for compliance
- Report any suspicious activity immediately

---

## Updates and Maintenance

### Stay Updated
- Monitor Angel One's developer portal for API updates
- Subscribe to API change notifications
- Test thoroughly after SmartAPI library updates

### Version Compatibility
- Current SmartAPI Python version: Check `requirements.txt`
- Recommended Python version: 3.8+
- Update regularly for bug fixes and security patches

---

**Last Updated**: March 2026  
**Version**: 1.0  
**Maintained by**: Stock Notification Manager Development Team
