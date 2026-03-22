"""
Test script for WhatsApp and Telegram messenger integration.

This script tests sending messages to numbers and groups using both messengers.
"""

import sys
import logging
from pathlib import Path

# Add project root to Python path so `src` is importable as a package
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.messenger_manager import MessengerManager, MessengerType
from src.messenger_base import MessageType

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create a single MessengerManager to reuse across tests (maintains session)
manager = MessengerManager()


def test_whatsapp_messenger():
    """Test WhatsApp messenger functionality."""
    logger.info("=" * 60)
    logger.info("Testing WhatsApp Messenger")
    logger.info("=" * 60)
    
    # Create/get WhatsApp messenger
    whatsapp = manager.create_messenger(MessengerType.WHATSAPP)
    
    if not whatsapp:
        logger.error("Failed to create WhatsApp messenger")
        return
    
    # Authenticate WhatsApp messenger (pywhatkit uses WhatsApp Web)
    if not whatsapp.authenticate({}):
        logger.error("WhatsApp authentication failed. Ensure pywhatkit is installed and WhatsApp Web is logged in.")
        return
    
    # Get test phone number from user
    print("\nWhatsApp Test")
    print("-" * 40)
    phone_number = input("Enter phone number with country code (e.g., +919876543210): ").strip()
    
    if not phone_number:
        logger.warning("No phone number provided, skipping WhatsApp test")
        return
    
    # Test sending message to number
    logger.info(f"Sending test message to {phone_number}")
    message = "Hello from Stock Notification Manager! This is a test message."
    
    receipt = whatsapp.send_message_to_number(phone_number, message, MessageType.TEXT)

    if receipt is None:
        logger.error("✗ No receipt returned. Message likely not sent. Check WhatsApp Web and pywhatkit.")
    elif getattr(receipt, 'success', None) or getattr(receipt, 'status', '') == 'sent':
        logger.info(f"✓ Message sent successfully at {receipt.timestamp}")
        logger.info(f"  Message: {getattr(receipt, 'message', '')}")
    else:
        logger.error(f"✗ Failed to send message: {getattr(receipt, 'error', 'Unknown error')}")
    
    # Test sending to group (optional)
    group_test = input("\nDo you want to test sending to a WhatsApp group? (y/n): ").strip().lower()
    if group_test == 'y':
        group_id = input("Enter WhatsApp group ID (usually phone number): ").strip()
        if group_id:
            logger.info(f"Sending test message to group {group_id}")
            group_receipt = whatsapp.send_message_to_group(group_id, message, MessageType.TEXT)
            
            if group_receipt is None:
                logger.error("✗ No receipt returned for group message. Check WhatsApp Web and pywhatkit.")
            elif getattr(group_receipt, 'success', None) or getattr(group_receipt, 'status', '') == 'sent':
                logger.info(f"✓ Group message sent successfully")
            else:
                logger.error(f"✗ Failed to send group message: {getattr(group_receipt, 'error', 'Unknown error')}")
    
    # Keep session active; do not disconnect here so subsequent tests reuse the session
    return


def test_telegram_messenger():
    """Test Telegram messenger functionality."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Telegram Messenger")
    logger.info("=" * 60)
    
    # Create/get Telegram messenger
    
    print("\nTelegram Test")
    print("-" * 40)
    print("To use Telegram messenger, you need:")
    print("1. Create a bot with @BotFather on Telegram")
    print("2. Get the bot token from @BotFather")
    print("3. Start a chat with your bot")
    print("4. Get your chat ID (use @userinfobot to get your chat ID)")
    print()
    
    bot_token = input("Enter Telegram bot token: ").strip()
    if not bot_token:
        logger.warning("No bot token provided, skipping Telegram test")
        return
    
    telegram = manager.create_messenger(MessengerType.TELEGRAM)
    if not telegram.authenticate({'bot_token': bot_token}):
        logger.error("Failed to authenticate Telegram bot")
        return
    
    # Test sending message to chat ID
    chat_id = input("Enter your Telegram chat ID (numeric): ").strip()
    
    if not chat_id:
        logger.warning("No chat ID provided, skipping Telegram message test")
        return
    
    logger.info(f"Sending test message to chat ID {chat_id}")
    message = "Hello from Stock Notification Manager! 📊\n\nThis is a test message from your stock notification bot."
    
    receipt = telegram.send_message_to_number(chat_id, message, MessageType.TEXT)
    if receipt is None:
        logger.error("✗ No receipt returned. Message likely not sent.")
    elif getattr(receipt, 'status', '') == 'sent' or getattr(receipt, 'success', None):
        logger.info(f"✓ Message sent successfully at {receipt.timestamp}")
        logger.info(f"  Message ID: {getattr(receipt, 'message_id', '')}")
    else:
        logger.error(f"✗ Failed to send message: {getattr(receipt, 'error', 'Unknown error')}")
    
    # Test sending to group (optional)
    group_test = input("\nDo you want to test sending to a Telegram group? (y/n): ").strip().lower()
    if group_test == 'y':
        group_id = input("Enter Telegram group chat ID: ").strip()
        if group_id:
            logger.info(f"Sending test message to group {group_id}")
            group_message = "📢 Group notification test from Stock Notification Manager!"
            group_receipt = telegram.send_message_to_group(group_id, group_message, MessageType.TEXT)
            
            if group_receipt is None:
                logger.error("✗ No receipt returned for group message.")
            elif getattr(group_receipt, 'status', '') == 'sent' or getattr(group_receipt, 'success', None):
                logger.info(f"✓ Group message sent successfully")
            else:
                logger.error(f"✗ Failed to send group message: {getattr(group_receipt, 'error', 'Unknown error')}")
    
    # Keep session active; do not disconnect here so subsequent tests reuse the session
    return


def main():
    """Main function to run messenger tests."""
    print("=" * 60)
    print("Stock Notification Manager - Messenger Tests")
    print("=" * 60)
    print()
    print("This script will test WhatsApp and Telegram messenger functionality.")
    print("You can test sending messages to numbers and groups.")
    print()
    
    while True:
        print("\nSelect messenger to test:")
        print("1. WhatsApp")
        print("2. Telegram")
        print("3. Both")
        print("0. Exit")
        print()
        
        choice = input("Enter your choice (0-3): ").strip()
        
        if choice == "0":
            logger.info("Exiting messenger tests")
            break
        elif choice == "1":
            test_whatsapp_messenger()
        elif choice == "2":
            test_telegram_messenger()
        elif choice == "3":
            test_whatsapp_messenger()
            test_telegram_messenger()
        else:
            print("Invalid choice. Please try again.")
    
    print("\nMessenger tests completed!")

    # Cleanup all messengers on exit
    manager.disconnect_all()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("\nTests interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error during tests: {e}", exc_info=True)
        sys.exit(1)
