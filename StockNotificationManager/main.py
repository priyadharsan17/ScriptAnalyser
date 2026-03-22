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
        
        # Get LTP for a few scripts
        logger.info("\n=== Getting Last Traded Prices ===")
        for script in nifty_50_scripts[:5]:  # Get LTP for first 5
            try:
                ltp_data = broker.get_ltp(script.symbol, script.exchange)
                if ltp_data:
                    logger.info(f"{script.symbol:<15} LTP: ₹{ltp_data.ltp:>10.2f}  "
                              f"Change: {ltp_data.change_percent:>+6.2f}%  "
                              f"Volume: {ltp_data.volume:>12,}")
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
    
    # Create broker manager (singleton instance for the app)
    broker_manager = BrokerManager()
    
    # Create backend instances
    screen_navigator = ScreenNavigator()
    login_backend = LoginBackend()
    home_backend = HomeBackend()
    
    # Register context properties
    root_context = engine.rootContext()
    root_context.setContextProperty("screenNavigator", screen_navigator)
    root_context.setContextProperty("loginBackend", login_backend)
    root_context.setContextProperty("homeBackend", home_backend)
    root_context.setContextProperty("brokerManager", broker_manager)
    
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
