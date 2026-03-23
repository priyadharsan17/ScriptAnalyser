import sys
import os
import json
import time
from pathlib import Path
import threading
import logging

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

# Import backend classes
from src.screen_navigator import ScreenNavigator
from src.login_backend import LoginBackend
from src.home_backend import HomeBackend
from src.broker_manager import BrokerManager, BrokerType

from src.messenger_manager import MessengerManager, MessengerType
from src.messenger_base import MessageType
from src.settings_manager import SettingsManager
from src.angel_one_settings_backend import AngelOneSettingsBackend
from src.telegram_settings_backend import TelegramSettingsBackend
from src.script_analysis_backend import ScriptAnalysisBackend

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Changed back to INFO for cleaner output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Nifty 50 stock symbols (as of common list)
NIFTY_50_SYMBOLS = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "HINDUNILVR",
    "ICICIBANK", "KOTAKBANK", "SBIN", "BHARTIARTL", "BAJFINANCE",
    "ITC", "ASIANPAINT", "LT", "AXISBANK", "DMART",
    "MARUTI", "SUNPHARMA", "TITAN", "ULTRACEMCO", "NESTLEIND",
    "WIPRO", "BAJAJFINSV", "ONGC", "NTPC", "POWERGRID",
    "TATASTEEL", "JSWSTEEL", "TECHM", "ADANIPORTS", "COALINDIA",
    "M&M", "HCLTECH", "TATAMOTORS", "INDUSINDBK", "DIVISLAB",
    "BAJAJ-AUTO", "SHREECEM", "GRASIM", "BRITANNIA", "HINDALCO",
    "APOLLOHOSP", "CIPLA", "DRREDDY", "EICHERMOT", "BPCL",
    "HEROMOTOCO", "TATACONSUM", "UPL", "SBILIFE", "ADANIENT"
]


def test_angel_one_integration():
    """
    Test function to demonstrate Angel One SmartAPI integration.
    This runs in a separate thread to avoid blocking the UI.
    """
    try:
        logger.info("=== Starting Angel One Integration Test ===")
        
        # Create broker manager
        manager = BrokerManager()
        logger.info("Broker manager created")
        
        # Load credentials from config file
        config_file = Path(__file__).parent / 'config' / 'angel_config.json'
        
        if not config_file.exists():
            logger.warning("Angel One config file not found!")
            logger.warning(f"Create {config_file} with your credentials")
            logger.warning("Copy from config/angel_config.example.json and fill in your details")
            logger.info("Skipping broker authentication test")
            
            # For demo purposes, create a broker instance without authentication
            broker = manager.create_broker(BrokerType.ANGEL_ONE)
            logger.info(f"Created broker: {broker.broker_name}")
            logger.info("Note: Broker is not authenticated. Real API calls will fail.")
            return
        
        # Read credentials from config file
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            credentials = {
                'api_key': config.get('api_key', ''),
                'client_id': config.get('client_id', ''),
                'password': config.get('password', ''),
                'totp': config.get('totp_secret') if config.get('totp_secret') and 
                        config.get('totp_secret') not in ['', 'optional_totp_secret', 'YOUR_TOTP_SECRET_HERE (optional)'] 
                        else None
            }
            
            # Validate credentials
            if not all([credentials['api_key'], credentials['client_id'], credentials['password']]):
                logger.error("Invalid credentials in config file!")
                logger.error("Ensure api_key, client_id, and password are set")
                return
                
            logger.info("Credentials loaded from config file")
            
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing config file: {e}")
            logger.error("Ensure angel_config.json is valid JSON")
            return
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
            return
        
        # Authenticate with Angel One
        logger.info("Attempting to authenticate with Angel One...")
        success = manager.set_active_broker(BrokerType.ANGEL_ONE, credentials)
        
        if not success:
            logger.error("Failed to authenticate with Angel One")
            logger.error("Check your credentials and ensure API access is enabled")
            return
        
        logger.info("✓ Successfully authenticated with Angel One")
        
        # Get the active broker
        broker = manager.active_broker
        logger.info(f"Active broker: {broker.broker_name}")
        logger.info(f"Status: {broker.status.value}")
        
        # Search for Nifty 50 scripts
        logger.info("\n=== Fetching Nifty 50 Scripts from NSE ===")
        nifty_50_scripts = []
        
        for symbol in NIFTY_50_SYMBOLS[:10]:  # Fetch first 10 for demo
            try:
                results = broker.search_scripts(symbol, "NSE")
                
                if results:
                    # Filter for -EQ (equity) scripts, or take first if no -EQ found
                    eq_script = next((s for s in results if s.symbol.endswith('-EQ')), results[0])
                    nifty_50_scripts.append(eq_script)
                    logger.info(f"✓ Found: {eq_script.symbol} - {eq_script.name}")
                else:
                    logger.warning(f"✗ Not found: {symbol}")
                    
                # Sleep to avoid API rate limits
                time.sleep(1)  # Increased to 1 second to avoid rate limiting
                    
            except Exception as e:
                logger.error(f"Error searching {symbol}: {e}")
                time.sleep(1)  # Also sleep on error
        
        # Print summary
        logger.info(f"\n=== Summary ===")
        logger.info(f"Total scripts fetched: {len(nifty_50_scripts)}")
        logger.info(f"\nNifty 50 Scripts (NSE):")
        logger.info("-" * 80)
        logger.info(f"{'Symbol':<15} {'Token':<10} {'Name':<40} {'Lot Size'}")
        logger.info("-" * 80)
        
        for script in nifty_50_scripts:
            logger.info(f"{script.symbol:<15} {script.token:<10} {script.name:<40} {script.lot_size}")
        
        logger.info("-" * 80)
        
        # Initialize messenger manager and WhatsApp messenger (authenticate once)
        msg_manager = MessengerManager()
        try:
            whatsapp = msg_manager.create_messenger(MessengerType.WHATSAPP)

            # Try to load Cloud API credentials from config/whatsapp_config.json
            wa_config_file = Path(__file__).parent / 'config' / 'whatsapp_config.json'
            wa_credentials = {}
            if wa_config_file.exists():
                try:
                    with open(wa_config_file, 'r') as wf:
                        wa_conf = json.load(wf)
                    wa_credentials = {
                        'use_cloud_api': bool(wa_conf.get('use_cloud_api', False)),
                        'phone_number_id': wa_conf.get('phone_number_id'),
                        'access_token': wa_conf.get('access_token')
                    }
                    logger.info(f"Loaded WhatsApp Cloud config from {wa_config_file}")
                except Exception as e:
                    logger.error(f"Failed to read WhatsApp config: {e}")

            # Authenticate with provided credentials (Cloud API if configured)
            if wa_credentials:
                if not whatsapp.authenticate(wa_credentials):
                    logger.error("WhatsApp authentication failed using provided config; falling back to pywhatkit (if available)")
            else:
                # No cloud config provided; use default authenticate (pywhatkit)
                if not whatsapp.authenticate({}):
                    logger.error("WhatsApp authentication failed (pywhatkit not available)")

            logger.info("WhatsApp messenger initialized for alerts")
        except Exception as e:
            logger.error(f"Failed to initialize WhatsApp messenger: {e}")

        # Initialize Telegram messenger if configuration exists
        try:
            tg_config_file = Path(__file__).parent / 'config' / 'telegram_config.json'
            if tg_config_file.exists():
                try:
                    with open(tg_config_file, 'r') as tf:
                        tg_conf = json.load(tf)

                    tg_credentials = {'bot_token': tg_conf.get('bot_token')}
                    telegram_ok = msg_manager.set_active_messenger(MessengerType.TELEGRAM, tg_credentials)
                    if telegram_ok:
                        logger.info(f"Telegram messenger authenticated")
                        tg = msg_manager.get_messenger(MessengerType.TELEGRAM)
                        # Optional test send
                        try:
                            send_test = bool(tg_conf.get('send_test_message', False))
                            chat_ids = tg_conf.get('chat_ids') or ([tg_conf.get('group_chat_id')] if tg_conf.get('group_chat_id') else [])
                            if send_test and chat_ids:
                                for cid in chat_ids:
                                    try:
                                        receipt = tg.send_message_to_group(str(cid), "Test broadcast — bot integrated successfully", MessageType.TEXT)
                                        if receipt and getattr(receipt, 'status', '') == 'sent':
                                            logger.info(f"Telegram test message sent to {cid}")
                                        else:
                                            logger.warning(f"Telegram test message failed for {cid}: {getattr(receipt, 'error', '')}")
                                    except Exception as e:
                                        logger.error(f"Error sending Telegram test message to {cid}: {e}")
                            else:
                                logger.info("Telegram config found but `send_test_message` is false or no chat_ids provided")
                        except Exception as e:
                            logger.error(f"Error during Telegram test send: {e}")
                    else:
                        logger.error("Telegram authentication failed; check bot token and ensure bot is added to group")
                except Exception as e:
                    logger.error(f"Failed to read Telegram config: {e}")
            else:
                logger.info("No Telegram config found; skipping Telegram initialization")
        except Exception as e:
            logger.error(f"Telegram initialization error: {e}")

        # Get LTP for a few scripts
        logger.info("\n=== Getting Last Traded Prices ===")
        for script in nifty_50_scripts[:5]:  # Get LTP for first 5
            try:
                ltp_data = broker.get_ltp(script.symbol, script.exchange)
                if ltp_data:
                    logger.info(f"{script.symbol:<15} LTP: ₹{ltp_data.ltp:>10.2f}  "
                              f"Change: {ltp_data.change_percent:>+6.2f}%  "
                              f"Volume: {ltp_data.volume:>12,}")
                    # Send alert message via WhatsApp
                    try:
                        alert_msg = (
                            f"Stock Alert - {script.symbol}\n"
                            f"Price: ₹{ltp_data.ltp:.2f}\n"
                            f"Change: {ltp_data.change_percent:+.2f}%\n"
                        )
                        receipt = whatsapp.send_message_to_number("+919442241270", alert_msg, MessageType.TEXT)
                        if receipt is None:
                            logger.warning(f"No receipt from WhatsApp for {script.symbol}")
                        elif getattr(receipt, 'status', '') == 'sent' or getattr(receipt, 'success', None):
                            logger.info(f"WhatsApp alert sent for {script.symbol}")
                        else:
                            logger.warning(f"WhatsApp alert failed for {script.symbol}: {getattr(receipt, 'error', '')}")
                    except Exception as e:
                        logger.error(f"Error sending WhatsApp alert for {script.symbol}: {e}")
            except Exception as e:
                logger.error(f"Error getting LTP for {script.symbol}: {e}")
        
        # Disconnect
        logger.info("\n=== Disconnecting ===")
        manager.disconnect_active_broker()
        logger.info("✓ Disconnected from Angel One")
        logger.info("=== Test Completed ===\n")
        
    except Exception as e:
        logger.error(f"Error in Angel One integration test: {e}", exc_info=True)


def main():
    """Main entry point for the Stock Notification Manager application."""
    
    # Start broker test in a separate thread (optional - for testing)
    # Uncomment the lines below to run the test
    # test_thread = threading.Thread(target=test_angel_one_integration, daemon=True)
    # test_thread.start()
    # logger.info("Angel One integration test started in background thread")
    
    # Create the application
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Stock Notification Manager")
    app.setOrganizationName("ScriptAnalyser")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Get the current directory
    current_dir = Path(__file__).parent

    # Initialize settings manager (use config/angel_config.json and a default)
    settings_file = current_dir / 'config' / 'angel_config.json'
    default_settings_file = current_dir / 'config' / 'angel_config.example.json'

    # Ensure default settings file exists
    if not default_settings_file.exists():
        try:
            default_settings_file.parent.mkdir(parents=True, exist_ok=True)
            default_settings_file.write_text(json.dumps({
                "api_key": "",
                "client_id": "",
                "password": "",
                "totp_secret": ""
            }, indent=2), encoding='utf-8')
            logger.info(f"Created minimal default Angel One settings at {default_settings_file}")
        except Exception as e:
            logger.error(f"Failed to create default Angel One settings file: {e}")

    # Instantiate SettingsManager
    try:
        angel_one_settings_manager = SettingsManager(settings_file, default_settings_file)
        logger.info("Angel One SettingsManager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Angel One SettingsManager: {e}")
        angel_one_settings_manager = None
    
    # Initialize Telegram settings manager
    telegram_settings_file = current_dir / 'config' / 'telegram_config.json'
    telegram_default_settings_file = current_dir / 'config' / 'telegram_config.example.json'

    # Ensure Telegram default settings file exists
    if not telegram_default_settings_file.exists():
        try:
            telegram_default_settings_file.parent.mkdir(parents=True, exist_ok=True)
            telegram_default_settings_file.write_text(json.dumps({
                "bot_token": "",
                "chat_ids": []
            }, indent=2), encoding='utf-8')
            logger.info(f"Created minimal default Telegram settings at {telegram_default_settings_file}")
        except Exception as e:
            logger.error(f"Failed to create default Telegram settings file: {e}")

    # Instantiate Telegram SettingsManager
    try:
        telegram_settings_manager = SettingsManager(telegram_settings_file, telegram_default_settings_file)
        logger.info("Telegram SettingsManager initialized")
    except Exception as e:
        logger.error(f"Failed to initialize Telegram SettingsManager: {e}")
        telegram_settings_manager = None
    
    # Create broker manager (singleton instance for the app)
    broker_manager = BrokerManager()
    
    # Create backend instances
    screen_navigator = ScreenNavigator()
    login_backend = LoginBackend()
    home_backend = HomeBackend()

    # Authenticate Angel One broker from settings and set active broker
    angel_broker = None
    if angel_one_settings_manager:
        try:
            settings = angel_one_settings_manager.get_settings()
            api_key = settings.get('api_key', '').strip()
            client_id = settings.get('client_id', '').strip()
            password = settings.get('password', '').strip()
            totp_secret = settings.get('totp_secret', '').strip()

            creds = {
                'api_key': api_key,
                'client_id': client_id,
                'password': password,
                'totp': totp_secret if totp_secret and totp_secret not in ['', 'optional_totp_secret', 'YOUR_TOTP_SECRET_HERE (optional)'] else None
            }

            # Try to set Angel One as the active broker (non-blocking here)
            if api_key and client_id and password:
                ok = broker_manager.set_active_broker(BrokerType.ANGEL_ONE, creds)
                if ok:
                    angel_broker = broker_manager.active_broker
                    logger.info("Angel One broker authenticated and active")
                else:
                    logger.warning("Angel One authentication failed at startup")
            else:
                logger.info("Angel One credentials incomplete; skipping automatic auth")
        except Exception as e:
            logger.error(f"Failed to initialize Angel One broker from settings: {e}")

    # Create Script Analysis backend and inject broker (may be None)
    script_analysis_backend = ScriptAnalysisBackend(angel_broker)
    
    # Create Angel One Settings backend
    angel_one_settings_backend = None
    if angel_one_settings_manager:
        angel_one_settings_backend = AngelOneSettingsBackend(angel_one_settings_manager)
    
    # Create Telegram Settings backend
    telegram_settings_backend = None
    if telegram_settings_manager:
        telegram_settings_backend = TelegramSettingsBackend(telegram_settings_manager)
    
    # Register context properties
    root_context = engine.rootContext()
    root_context.setContextProperty("screenNavigator", screen_navigator)
    root_context.setContextProperty("loginBackend", login_backend)
    root_context.setContextProperty("homeBackend", home_backend)
    root_context.setContextProperty("angelOneSettingsBackend", angel_one_settings_backend)
    root_context.setContextProperty("telegramSettingsBackend", telegram_settings_backend)
    root_context.setContextProperty("scriptAnalysisBackend", script_analysis_backend)
    
    # Add import path for QML modules
    engine.addImportPath(str(current_dir / "qml"))
    
    # Load the main QML file
    qml_file = current_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if the QML file loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return -1
    
    # Run the application
    result = app.exec()
    
    # Cleanup broker connections before exit
    broker_manager.cleanup()
    
    return result


def test_mode():
    """
    Run only the Angel One integration test without starting the GUI.
    Useful for testing broker integration independently.
    """
    logger.info("Running in TEST MODE (no GUI)")
    test_angel_one_integration()

if __name__ == "__main__":
    # Check if running in test mode
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_mode()
    else:
        sys.exit(main())
