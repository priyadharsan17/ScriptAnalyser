# Broker Integration Procedures

## Overview
This document outlines the procedures for integrating and using different brokers with the Stock Notification Manager.

---

## Table of Contents
1. [General Broker Setup](#general-broker-setup)
2. [Angel One Integration](#angel-one-integration)
3. [Motilal Oswal Integration](#motilal-oswal-integration)
4. [Adding New Broker](#adding-new-broker)
5. [Common Operations](#common-operations)

---

## General Broker Setup

### Architecture Overview

The broker integration follows the **Strategy Pattern** with:
- **BrokerBase**: Abstract base class defining the interface
- **Concrete Brokers**: Angel One, Motilal Oswal implementations
- **BrokerManager**: Factory class for broker lifecycle management

### File Structure

```
src/
├── broker_base.py          # Abstract base class
├── angel_one_broker.py     # Angel One implementation
├── motilal_oswal_broker.py # Motilal Oswal implementation
├── broker_manager.py       # Factory and manager
└── screen_navigator.py     # UI navigation
```

---

## Angel One Integration

### Procedure: Connect to Angel One

#### Step 1: Prepare Credentials

```python
credentials = {
    'api_key': 'YOUR_API_KEY',
    'client_id': 'YOUR_CLIENT_ID',
    'password': 'YOUR_PASSWORD',
    'totp': 'CURRENT_TOTP_CODE'  # Optional
}
```

#### Step 2: Initialize Manager

```python
from src.broker_manager import BrokerManager, BrokerType

manager = BrokerManager()
```

#### Step 3: Authenticate

```python
success = manager.set_active_broker(BrokerType.ANGEL_ONE, credentials)

if success:
    print("✓ Connected to Angel One")
    broker = manager.active_broker
    print(f"Broker: {broker.broker_name}")
    print(f"Status: {broker.status.value}")
else:
    print("✗ Authentication failed")
```

#### Step 4: Verify Connection

```python
# Check connection status
if broker.is_connected:
    print("✓ Broker is connected")
    
    # Get session info
    print(f"Session Token: {broker._session_token[:10]}...")
    print(f"Feed Token: {broker._feed_token[:10]}...")
```

### Procedure: Fetch Market Data

#### Get Script List

```python
# Get all NSE scripts
nse_scripts = broker.get_script_list("NSE")
print(f"Found {len(nse_scripts)} NSE scripts")

# Get all scripts (all exchanges)
all_scripts = broker.get_script_list()
print(f"Total scripts: {len(all_scripts)}")
```

#### Search for Specific Stock

```python
# Search for Reliance
results = broker.search_scripts("RELIANCE", "NSE")

for script in results:
    print(f"Symbol: {script.symbol}")
    print(f"Token: {script.token}")
    print(f"Name: {script.name}")
    print(f"Exchange: {script.exchange}")
    print("-" * 40)
```

#### Get Last Traded Price

```python
# Get LTP for single script
ltp_data = broker.get_ltp("RELIANCE", "NSE")

if ltp_data:
    print(f"Symbol: {ltp_data.symbol}")
    print(f"LTP: ₹{ltp_data.ltp}")
    print(f"Volume: {ltp_data.volume:,}")
    print(f"Change: ₹{ltp_data.change}")
    print(f"Change %: {ltp_data.change_percent}%")
    print(f"Time: {ltp_data.timestamp}")
```

#### Get Bulk LTP

```python
# Get LTP for multiple scripts
scripts = [
    ("RELIANCE", "NSE"),
    ("TCS", "NSE"),
    ("INFY", "NSE"),
    ("HDFCBANK", "NSE")
]

ltp_bulk = broker.get_ltp_bulk(scripts)

for symbol, data in ltp_bulk.items():
    print(f"{symbol}: ₹{data.ltp} ({data.change_percent:+.2f}%)")
```

### Procedure: Monitor Active Scripts

#### Add Scripts to Watchlist

```python
# Add individual scripts
broker.add_active_script("RELIANCE", "NSE")
broker.add_active_script("TCS", "NSE")
broker.add_active_script("INFY", "NSE")

# Verify
active_scripts = broker.active_scripts
print(f"Monitoring {len(active_scripts)} scripts:")
for script in active_scripts:
    print(f"  - {script.symbol} ({script.exchange})")
```

#### Remove Scripts

```python
# Remove specific script
broker.remove_active_script("INFY", "NSE")

# Clear all
broker.clear_active_scripts()
```

### Procedure: Subscribe to Live Feed

#### Setup WebSocket Connection

```python
def on_live_data(data):
    """
    Callback function for live market data.
    
    Args:
        data: Market data message from WebSocket
    """
    try:
        print(f"Live Data: {data}")
        # Process the data here
        # Extract LTP, volume, etc.
    except Exception as e:
        print(f"Error processing data: {e}")

# Subscribe
success = broker.subscribe_live_data(on_live_data)
if success:
    print("✓ Subscribed to live market data")
else:
    print("✗ Failed to subscribe")
```

#### Unsubscribe

```python
# Unsubscribe when done
broker.unsubscribe_live_data()
print("✓ Unsubscribed from live data")
```

### Procedure: Disconnect

```python
# Properly disconnect
success = broker.disconnect()
if success:
    print("✓ Disconnected from Angel One")
else:
    print("✗ Disconnect failed")

# Or use manager
manager.disconnect_active_broker()
```

---

## Motilal Oswal Integration

### Procedure: Connect to Motilal Oswal

#### Step 1: Prepare Credentials

```python
credentials = {
    'vendor_code': 'YOUR_VENDOR_CODE',
    'api_key': 'YOUR_API_KEY',
    'password': 'YOUR_PASSWORD'
}
```

#### Step 2: Authenticate

```python
from src.broker_manager import BrokerManager, BrokerType

manager = BrokerManager()
success = manager.set_active_broker(BrokerType.MOTILAL_OSWAL, credentials)

if success:
    print("✓ Connected to Motilal Oswal")
    broker = manager.active_broker
else:
    print("✗ Authentication failed")
```

#### Step 3: Use Same Operations

All operations (search, LTP, active scripts, etc.) work the same way as Angel One due to the common interface.

---

## Adding New Broker

### Procedure: Implement New Broker

#### Step 1: Create Broker Class

Create a new file `src/your_broker.py`:

```python
from typing import List, Dict, Optional, Any
from .broker_base import BrokerBase, BrokerStatus, Script, LTPData
import logging

logger = logging.getLogger(__name__)

class YourBroker(BrokerBase):
    """Your broker implementation."""
    
    def __init__(self):
        super().__init__("Your Broker Name")
        # Initialize broker-specific attributes
    
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """Implement authentication logic."""
        try:
            # Your authentication code here
            self._status = BrokerStatus.CONNECTED
            return True
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            self._status = BrokerStatus.ERROR
            return False
    
    def disconnect(self) -> bool:
        """Implement disconnection logic."""
        # Your disconnection code here
        self._status = BrokerStatus.DISCONNECTED
        return True
    
    def get_script_list(self, exchange: Optional[str] = None) -> List[Script]:
        """Implement script list retrieval."""
        # Your implementation
        pass
    
    def search_scripts(self, query: str, exchange: Optional[str] = None) -> List[Script]:
        """Implement script search."""
        # Your implementation
        pass
    
    def get_ltp(self, symbol: str, exchange: str) -> Optional[LTPData]:
        """Implement LTP retrieval."""
        # Your implementation
        pass
    
    def get_ltp_bulk(self, scripts: List[tuple]) -> Dict[str, LTPData]:
        """Implement bulk LTP retrieval."""
        # Your implementation
        pass
    
    def add_active_script(self, symbol: str, exchange: str) -> bool:
        """Implement add to watchlist."""
        # Your implementation
        pass
    
    def remove_active_script(self, symbol: str, exchange: str) -> bool:
        """Implement remove from watchlist."""
        # Your implementation
        pass
    
    def subscribe_live_data(self, callback) -> bool:
        """Implement WebSocket subscription."""
        # Your implementation
        pass
    
    def unsubscribe_live_data(self) -> bool:
        """Implement WebSocket unsubscription."""
        # Your implementation
        pass
```

#### Step 2: Register in BrokerManager

Edit `src/broker_manager.py`:

```python
from .your_broker import YourBroker

class BrokerType(Enum):
    ANGEL_ONE = "angel_one"
    MOTILAL_OSWAL = "motilal_oswal"
    YOUR_BROKER = "your_broker"  # Add this

class BrokerManager:
    _BROKER_REGISTRY = {
        BrokerType.ANGEL_ONE: AngelOneBroker,
        BrokerType.MOTILAL_OSWAL: MotilalOswalBroker,
        BrokerType.YOUR_BROKER: YourBroker,  # Add this
    }
```

#### Step 3: Test Integration

```python
# Test your broker
manager = BrokerManager()
success = manager.set_active_broker(BrokerType.YOUR_BROKER, credentials)

if success:
    broker = manager.active_broker
    # Test operations
    scripts = broker.search_scripts("TEST")
    print(f"Found {len(scripts)} scripts")
```

---

## Common Operations

### Error Handling

```python
from src.broker_base import BrokerStatus

try:
    success = manager.set_active_broker(BrokerType.ANGEL_ONE, credentials)
    
    if not success:
        broker = manager.active_broker
        if broker.status == BrokerStatus.ERROR:
            print("Authentication error")
        elif broker.status == BrokerStatus.DISCONNECTED:
            print("Not connected")
            
except Exception as e:
    print(f"Error: {e}")
```

### Logging

```python
import logging

# Enable detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('broker.log'),
        logging.StreamHandler()
    ]
)
```

### Cleanup

```python
# Always cleanup when done
try:
    # Your operations
    pass
finally:
    manager.cleanup()
```

---

## Best Practices

### 1. Connection Management
- Always check `is_connected` before operations
- Implement connection retry logic
- Handle session expiry gracefully

### 2. Error Handling
- Catch and log all exceptions
- Provide meaningful error messages
- Implement fallback mechanisms

### 3. Performance
- Cache script lists (refresh periodically)
- Use bulk operations when possible
- Implement rate limiting

### 4. Security
- Never log credentials
- Use secure credential storage
- Implement proper authentication

### 5. Testing
- Test each broker independently
- Mock external API calls for unit tests
- Implement integration tests

---

## Troubleshooting Checklist

- [ ] Credentials are correct
- [ ] API access is enabled
- [ ] Internet connection is stable
- [ ] Broker server is operational
- [ ] Rate limits not exceeded
- [ ] Session token is valid
- [ ] Required libraries are installed
- [ ] Firewall allows connections
- [ ] Correct exchange and symbol format
- [ ] Sufficient logging enabled

---

**Last Updated**: March 2026  
**Maintained by**: Stock Notification Manager Development Team
