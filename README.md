# ScriptAnalyser

Stock Notification Manager - A PySide6 application for monitoring stock prices with broker integration.

## Features

- 🎨 Modern UI with light theme and drop shadows
- 🔐 Secure login system
- 📊 Dashboard with feature cards
- 🔌 Broker integration (Angel One SmartAPI)
- 📈 Real-time stock monitoring
- � Messenger integration (WhatsApp & Telegram)
- 🔔 Price notifications via WhatsApp/Telegram

---

## Setup Virtual Environment

**From repo root:** open PowerShell and run:

```powershell
cd StockNotificationManager
.\setup_venv_and_freeze.bat
```

This creates a `.venv` folder, installs `PySide6`, and writes `requirements.txt` into the `StockNotificationManager` folder.

**Activate the venv later:**

```powershell
.\.venv\Scripts\activate.bat
```

**Notes:** Ensure `python` (3.8+) is on your PATH. If the script fails, you can create the venv and install manually:

```powershell
python -m venv .venv
.\.venv\Scripts\activate.bat
pip install PySide6 smartapi-python pywhatkit python-telegram-bot
pip freeze > requirements.txt
```

---

## Running the Application

### Normal Mode (with GUI)

```powershell
cd StockNotificationManager
.\.venv\Scripts\activate.bat
python main.py
```

### Test Mode (Angel One Integration Test)

```powershell
cd StockNotificationManager
.\.venv\Scripts\activate.bat

# Setup config file
copy config\angel_config.example.json config\angel_config.json
notepad config\angel_config.json  # Fill in your credentials

# Run the test
python test_broker.py
```

Or use the test flag:
```powershell
python main.py --test
```

See `Documentation/Running_Tests.md` for detailed test instructions.

---

## Broker Setup

### Angel One SmartAPI

1. Register at [Angel One SmartAPI Portal](https://smartapi.angelbroking.com/)
2. Create an app and get API credentials
3. Enable API trading in your Angel One account
4. Install smartapi-python: `pip install smartapi-python`

**Complete setup guide:** See `Documentation/AngelOne_SmartAPI_Setup.md`

**Integration procedures:** See `Documentation/Broker_Integration_Procedures.md`

### WhatsApp & Telegram Messengers

**WhatsApp Setup:**
1. Login to WhatsApp Web on your browser
2. Keep session active
3. No API credentials needed

**Telegram Setup:**
1. Create a bot with [@BotFather](https://t.me/BotFather)
2. Get bot token from @BotFather
3. Get your chat ID from [@userinfobot](https://t.me/userinfobot)

**Testing:**
```powershell
python test_messengers.py
```

**Complete guide:** See `Documentation/Messenger_Integration.md`

---

## Project Structure

```
StockNotificationManager/
├── main.py                 # Application entry point
├── test_broker.py          # Broker integration test script
├── main.qml                # Main QML window
├── setup_venv_and_freeze.bat  # Setup script
├── requirements.txt        # Python dependencies
├── test_messengers.py      # Messenger integration test
├── src/                    # Python backend
│   ├── screen_navigator.py
│   ├── login_backend.py
│   ├── home_backend.py
│   ├── broker_base.py      # Abstract broker interface
│   ├── angel_one_broker.py # Angel One implementation
│   ├── motilal_oswal_broker.py
│   ├── broker_manager.py   # Broker factory
│   ├── messenger_base.py   # Abstract messenger interface
│   ├── whatsapp_messenger.py # WhatsApp implementation
│   ├── telegram_messenger.py # Telegram implementation
│   └── messenger_manager.py  # Messenger factory
├── qml/                    # QML UI files
│   ├── Theme.qml          # App theme
│   ├── Login.qml
│   ├── HomeScreen.qml
│   ├── CustomButton.qml
│   └── CustomTextField.qml
├── assets/                 # Icons and images
└── Documentation/          # Guides and procedures
    ├── AngelOne_SmartAPI_Setup.md
    ├── Broker_Integration_Procedures.md
    ├── Messenger_Integration.md
    └── Running_Tests.md
```

---

## Documentation

- **[Angel One Setup Guide](StockNotificationManager/Documentation/AngelOne_SmartAPI_Setup.md)** - Complete SmartAPI registration and setup
- **[Broker Integration](StockNotificationManager/Documentation/Broker_Integration_Procedures.md)** - Technical procedures for broker usage
- **[Messenger Integration](StockNotificationManager/Documentation/Messenger_Integration.md)** - WhatsApp & Telegram setup and usage
- **[Running Tests](StockNotificationManager/Documentation/Running_Tests.md)** - How to run integration tests

---

## Dependencies

- Python 3.8+
- PySide6 (Qt6 for Python)
- smartapi-python (Angel One API)
- pywhatkit (WhatsApp automation)
- python-telegram-bot (Telegram Bot API)

---

## Security Notes

⚠️ **Never commit credentials to version control!**

- Store credentials in `config/angel_config.json` (gitignored)
- See `config/angel_config.example.json` for config format
- Rotate API keys regularly
- Never hardcode credentials in source files

---

## License

This project is for personal use and educational purposes.