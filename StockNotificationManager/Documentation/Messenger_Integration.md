# Messenger Integration - WhatsApp & Telegram

## Overview

The Stock Notification Manager includes a messenger abstraction system that supports sending notifications via WhatsApp and Telegram. The architecture follows the same OOP design pattern as the broker integration system.

---

## Architecture

### 1. Base Class (`src/messenger_base.py`)

**Abstract class** `MessengerBase` defining the interface for all messengers:

#### Enums:
- `MessengerStatus`: NOT_CONNECTED, CONNECTED, SENDING, ERROR
- `MessageType`: TEXT, IMAGE, VIDEO, AUDIO, DOCUMENT, LOCATION

#### Data Classes:
- `MessageReceipt`: Contains success status, timestamp, message_id, message text, and error info

#### Abstract Methods:
All messenger implementations must provide:
- `send_message_to_number(phone_number, message, message_type)` - Send to individual
- `send_message_to_group(group_id, message, message_type)` - Send to group
- `send_message_to_channel(channel_id, message, message_type)` - Send to channel
- `get_groups()` - List available groups
- `get_channels()` - List available channels
- `disconnect()` - Cleanup and disconnect

### 2. WhatsApp Implementation (`src/whatsapp_messenger.py`)

**Concrete class** using `pywhatkit` library for WhatsApp Web automation:

#### Features:
- ✅ Send text messages to phone numbers
- ✅ Send text messages to groups
- ✅ Send images with captions
- ✅ Automatic WhatsApp Web browser opening
- ⚠️ Channels not supported (WhatsApp Web limitation)

#### Requirements:
- WhatsApp Web must be logged in on default browser
- Browser will open automatically for each message
- Requires GUI environment (not headless)

#### Supported Message Types:
- `TEXT` - Plain text messages
- `IMAGE` - Images with optional caption

### 3. Telegram Implementation (`src/telegram_messenger.py`)

**Concrete class** using `python-telegram-bot` library (Bot API):

#### Features:
- ✅ Send messages to users (via chat_id)
- ✅ Send messages to groups
- ✅ Send messages to channels
- ✅ Full media support (text, images, documents, videos, audio)
- ✅ HTML formatting support
- ✅ Works headless (no browser required)

#### Supported Message Types:
- `TEXT` - Plain text with HTML formatting
- `IMAGE` - Photos with captions
- `DOCUMENT` - File attachments
- `VIDEO` - Video files
- `AUDIO` - Audio files

### 4. Messenger Manager (`src/messenger_manager.py`)

**Factory pattern** for creating and managing messenger instances:

#### Features:
- `MessengerType` enum: WHATSAPP, TELEGRAM
- Create messenger instances: `create_messenger(messenger_type, **kwargs)`
- Active messenger management: `set_active_messenger(messenger_type)`
- Batch operations: `disconnect_all()`, `cleanup()`
- Automatic cleanup on application exit

---

## Installation

### Required Packages

Install the messenger dependencies:

```powershell
cd StockNotificationManager
.\.venv\Scripts\activate.bat
pip install pywhatkit python-telegram-bot
pip freeze > requirements.txt
```

### Package Details:
- **pywhatkit** (5.4): WhatsApp Web automation via browser
- **python-telegram-bot** (22.7): Telegram Bot API wrapper

---

## WhatsApp Setup

### Prerequisites:
1. WhatsApp account with active phone number
2. WhatsApp Web access on your default browser
3. Browser must support WhatsApp Web (Chrome, Firefox, Edge, etc.)

### Configuration:
1. **Login to WhatsApp Web:**
   - Open browser and go to [web.whatsapp.com](https://web.whatsapp.com)
   - Scan QR code with your phone
   - Keep session logged in

2. **No API credentials required** - WhatsApp uses browser automation

3. **Important Notes:**
   - Browser will open automatically when sending messages
   - Message will be sent after a delay (default 15 seconds)
   - Do not close the browser window during sending
   - Works only on machines with GUI (not headless servers)

### Phone Number Format:
- **Required format:** Country code + phone number (no spaces/dashes)
- **Examples:**
  - India: `+919876543210`
  - USA: `+11234567890`
  - UK: `+447911123456`

### Group ID Format:
- Use the phone number associated with the group
- Same format as individual numbers

---

## Telegram Setup

### 1. Create a Telegram Bot

**Step-by-step:**

1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Start a chat and send `/newbot`
3. Follow the prompts:
   - Enter a name for your bot (e.g., "Stock Notification Bot")
   - Enter a username (must end with 'bot', e.g., "stock_notify_bot")
4. **Copy the bot token** - looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`
5. **Save this token securely** - you'll need it to send messages

### 2. Get Your Chat ID

**Method 1: Using @userinfobot**
1. Open Telegram and search for [@userinfobot](https://t.me/userinfobot)
2. Start the bot
3. It will reply with your chat ID (a number)

**Method 2: Using Your Bot**
1. Start a chat with your newly created bot
2. Send any message to it
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for `"chat":{"id":123456789}` in the JSON response
5. The number is your chat ID

### 3. Get Group/Channel IDs

**For Groups:**
1. Add your bot to the group (as admin if possible)
2. Send a message in the group
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the group chat ID (will be negative, e.g., `-1001234567890`)

**For Channels:**
1. Add your bot as an administrator to the channel
2. Post a message in the channel
3. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the channel ID (starts with `-100`, e.g., `-1001234567890`)

### 4. Configuration

Store your bot token securely:

```json
{
  "telegram": {
    "bot_token": "1234567890:ABCdefGHIjklMNOpqrsTUVwxyz",
    "default_chat_id": "123456789"
  }
}
```

---

## Usage Examples

### Example 1: Send WhatsApp Message to Number

```python
from messenger_manager import MessengerManager, MessengerType
from messenger_base import MessageType

# Create messenger manager
manager = MessengerManager()

# Create WhatsApp messenger
whatsapp = manager.create_messenger(MessengerType.WHATSAPP)

# Send message
receipt = whatsapp.send_message_to_number(
    phone_number="+919876543210",
    message="RELIANCE-EQ reached ₹1500! 📈",
    message_type=MessageType.TEXT
)

if receipt.success:
    print(f"Message sent at {receipt.timestamp}")
else:
    print(f"Failed: {receipt.error}")

# Cleanup
manager.disconnect_all()
```

### Example 2: Send Telegram Message to User

```python
from messenger_manager import MessengerManager, MessengerType
from messenger_base import MessageType

# Create messenger manager
manager = MessengerManager()

# Create Telegram messenger with bot token
telegram = manager.create_messenger(
    MessengerType.TELEGRAM,
    bot_token="1234567890:ABCdefGHIjklMNOpqrsTUVwxyz"
)

# Send message (chat_id is a string)
receipt = telegram.send_message_to_number(
    phone_number="123456789",  # This is actually chat_id for Telegram
    message="<b>Stock Alert!</b>\n\nRELIANCE-EQ: ₹1500.00 (+2.5%)",
    message_type=MessageType.TEXT
)

if receipt.success:
    print(f"Message sent! Message ID: {receipt.message_id}")
else:
    print(f"Failed: {receipt.error}")

# Cleanup
manager.disconnect_all()
```

### Example 3: Send to Telegram Group/Channel

```python
from messenger_manager import MessengerManager, MessengerType
from messenger_base import MessageType

# Create messenger
manager = MessengerManager()
telegram = manager.create_messenger(
    MessengerType.TELEGRAM,
    bot_token="YOUR_BOT_TOKEN"
)

# Send to group
group_receipt = telegram.send_message_to_group(
    group_id="-1001234567890",
    message="📊 <b>Nifty 50 Update</b>\n\nCurrent: 21,500\nChange: +150 (+0.7%)",
    message_type=MessageType.TEXT
)

# Send to channel
channel_receipt = telegram.send_message_to_channel(
    channel_id="-1001234567890",
    message="🔔 Daily Market Summary - March 22, 2026",
    message_type=MessageType.TEXT
)

manager.disconnect_all()
```

### Example 4: Send Image with WhatsApp

```python
from messenger_manager import MessengerManager, MessengerType
from messenger_base import MessageType

manager = MessengerManager()
whatsapp = manager.create_messenger(MessengerType.WHATSAPP)

# Send image
receipt = whatsapp.send_message_to_number(
    phone_number="+919876543210",
    message="path/to/chart.png|Stock chart for RELIANCE",  # Format: path|caption
    message_type=MessageType.IMAGE
)

manager.disconnect_all()
```

### Example 5: Multiple Messengers

```python
from messenger_manager import MessengerManager, MessengerType
from messenger_base import MessageType

# Create manager
manager = MessengerManager()

# Create both messengers
whatsapp = manager.create_messenger(MessengerType.WHATSAPP)
telegram = manager.create_messenger(
    MessengerType.TELEGRAM,
    bot_token="YOUR_BOT_TOKEN"
)

# Send same alert to both
alert_message = "🚨 NIFTY 50 crossed 22,000!"

whatsapp_receipt = whatsapp.send_message_to_number(
    "+919876543210", alert_message, MessageType.TEXT
)

telegram_receipt = telegram.send_message_to_number(
    "123456789", alert_message, MessageType.TEXT
)

# Cleanup all
manager.disconnect_all()
```

---

## Testing

### Test Script: `test_messengers.py`

Run the interactive test script to verify messenger functionality:

```powershell
cd StockNotificationManager
.\.venv\Scripts\activate.bat
python test_messengers.py
```

The test script provides:
1. **Interactive menu** to choose messenger
2. **WhatsApp test** - prompts for phone number and sends test message
3. **Telegram test** - prompts for bot token and chat ID
4. **Group testing** - optional group message testing
5. **Detailed logging** - shows success/failure status

### Manual Testing Steps:

**WhatsApp:**
1. Ensure WhatsApp Web is logged in
2. Run test script and select WhatsApp
3. Enter phone number with country code
4. Browser will open and send message
5. Check WhatsApp on phone to verify

**Telegram:**
1. Create bot with @BotFather
2. Get bot token
3. Get your chat ID from @userinfobot
4. Run test script and select Telegram
5. Enter bot token and chat ID
6. Check Telegram to verify message

---

## Integration with Broker System

### Example: Stock Price Alert

```python
from broker_manager import BrokerManager, BrokerType
from messenger_manager import MessengerManager, MessengerType
from messenger_base import MessageType
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize managers
broker_mgr = BrokerManager()
msg_mgr = MessengerManager()

# Create broker and messenger
angel = broker_mgr.create_broker(BrokerType.ANGEL_ONE)
telegram = msg_mgr.create_messenger(
    MessengerType.TELEGRAM,
    bot_token="YOUR_BOT_TOKEN"
)

# Authenticate with broker
if angel.authenticate():
    logger.info("Broker authenticated")
    
    # Search for stock
    scripts = angel.search_scripts("RELIANCE")
    if scripts:
        script = scripts[0]
        logger.info(f"Found: {script.trading_symbol}")
        
        # Get LTP
        ltp_data = angel.get_ltp(script.exchange, script.token)
        if ltp_data:
            price = ltp_data.ltp
            logger.info(f"Current price: ₹{price}")
            
            # Send alert if price crosses threshold
            threshold = 1500.00
            if price >= threshold:
                alert = f"🚨 <b>Price Alert!</b>\n\n"
                alert += f"Stock: {script.trading_symbol}\n"
                alert += f"Price: ₹{price:.2f}\n"
                alert += f"Threshold: ₹{threshold:.2f}"
                
                receipt = telegram.send_message_to_number(
                    "YOUR_CHAT_ID",
                    alert,
                    MessageType.TEXT
                )
                
                if receipt.success:
                    logger.info("Alert sent successfully!")
                else:
                    logger.error(f"Alert failed: {receipt.error}")

# Cleanup
broker_mgr.disconnect_all()
msg_mgr.disconnect_all()
```

---

## Troubleshooting

### WhatsApp Issues

**Problem:** Browser doesn't open
- **Solution:** Check default browser settings, ensure browser is installed

**Problem:** Message not sent
- **Solution:** Ensure WhatsApp Web is logged in, check phone number format

**Problem:** "Not logged in" error
- **Solution:** Open WhatsApp Web manually and scan QR code

**Problem:** Slow sending
- **Solution:** Default delay is 15 seconds, adjust using `tab_close` parameter

### Telegram Issues

**Problem:** "Unauthorized" error
- **Solution:** Check bot token is correct, create new bot if needed

**Problem:** "Chat not found" error
- **Solution:** Start a conversation with the bot before sending messages

**Problem:** Can't send to group
- **Solution:** Add bot to group first, make it admin if needed

**Problem:** Can't send to channel
- **Solution:** Add bot as administrator to the channel

**Problem:** HTML formatting not working
- **Solution:** Use proper HTML tags: `<b>`, `<i>`, `<u>`, `<code>`, `<pre>`

---

## Comparison: WhatsApp vs Telegram

| Feature | WhatsApp | Telegram |
|---------|----------|----------|
| **Setup Complexity** | Easy (no API) | Medium (bot token required) |
| **Browser Required** | Yes | No |
| **Headless Support** | No | Yes |
| **Message Types** | Text, Image | Text, Image, Video, Audio, Document |
| **Formatting** | Plain text | HTML/Markdown |
| **Groups** | ✅ Yes | ✅ Yes |
| **Channels** | ❌ No | ✅ Yes |
| **Delivery Speed** | Slower (browser) | Fast (API) |
| **Reliability** | Medium | High |
| **Best For** | Personal notifications | Automated alerts, channels |

---

## Best Practices

### 1. Rate Limiting
- **WhatsApp:** Avoid sending too many messages quickly (can trigger spam detection)
- **Telegram:** Bot API limits: 30 messages/second to different chats

### 2. Error Handling
Always check receipt status:
```python
receipt = messenger.send_message_to_number(phone, message, MessageType.TEXT)
if not receipt.success:
    logger.error(f"Failed to send: {receipt.error}")
    # Implement retry logic or alert admin
```

### 3. Credential Security
- Store bot tokens in config files (gitignored)
- Never commit credentials to version control
- Use environment variables for production

### 4. Message Formatting
- Keep messages concise and clear
- Use emojis for better visibility: 📊 📈 📉 🚨 ⚠️ ✅ ❌
- For Telegram, use HTML for formatting

### 5. Cleanup
Always cleanup resources:
```python
try:
    # Send messages
    pass
finally:
    messenger_manager.disconnect_all()
```

---

## Future Enhancements

### Planned Features:
- 📱 **SMS Integration** - Send alerts via SMS
- 📧 **Email Integration** - Send detailed reports via email
- 🔔 **Push Notifications** - Native desktop/mobile notifications
- 📊 **Rich Media** - Send charts and graphs
- 🤖 **Interactive Bots** - Two-way communication for commands
- 📅 **Scheduled Messages** - Send alerts at specific times
- 🎯 **Smart Routing** - Auto-select best messenger based on context

### Contribution:
Want to add support for more messengers? Follow the pattern:
1. Inherit from `MessengerBase`
2. Implement all abstract methods
3. Add to `MessengerType` enum
4. Update `MessengerManager.create_messenger()`

---

## Summary

The messenger integration provides:
- ✅ **Abstraction** - Easy to add new messengers
- ✅ **Flexibility** - Choose WhatsApp or Telegram based on needs
- ✅ **Reliability** - Error handling and receipts
- ✅ **Ease of Use** - Simple API for sending messages
- ✅ **Integration** - Works seamlessly with broker system

Perfect for sending real-time stock alerts, daily summaries, and price notifications! 📊📱
