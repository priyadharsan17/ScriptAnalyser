# Angel One SmartAPI Test Script
# This script demonstrates the broker integration without running the GUI

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Run the test mode
from main import test_mode

if __name__ == "__main__":
    print("=" * 80)
    print("Stock Notification Manager - Angel One Integration Test")
    print("=" * 80)
    print()
    print("This script will test the Angel One SmartAPI integration.")
    print()
    print("To run with real credentials, create 'config/angel_config.json':")
    print("  1. Copy config/angel_config.example.json to config/angel_config.json")
    print("  2. Fill in your Angel One credentials")
    print("  3. Run this script")
    print()
    print("Required fields in config/angel_config.json:")
    print('  - api_key: Your API key from Angel One')
    print('  - client_id: Your client ID')
    print('  - password: Your password')
    print('  - totp_secret: Your TOTP secret (optional)')
    print()
    print("=" * 80)
    print()
    
    # Run the test
    test_mode()
