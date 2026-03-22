"""
Base abstract class for stock broker integration.
Defines the interface that all broker implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from enum import Enum


class BrokerStatus(Enum):
    """Enumeration for broker connection status."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


@dataclass
class Script:
    """Data class representing a trading script/instrument."""
    symbol: str
    token: str
    exchange: str
    name: str
    lot_size: int
    tick_size: float


@dataclass
class LTPData:
    """Data class representing Last Traded Price data."""
    symbol: str
    ltp: float
    volume: int
    timestamp: str
    change: float
    change_percent: float


class BrokerBase(ABC):
    """
    Abstract base class for stock broker integration.
    All broker implementations must inherit from this class and implement all abstract methods.
    """
    
    def __init__(self, broker_name: str):
        """
        Initialize the broker base class.
        
        Args:
            broker_name: Name of the broker
        """
        self._broker_name = broker_name
        self._status = BrokerStatus.DISCONNECTED
        self._active_scripts: List[Script] = []
        self._credentials: Optional[Dict[str, Any]] = None
    
    @property
    def broker_name(self) -> str:
        """Get the broker name."""
        return self._broker_name
    
    @property
    def status(self) -> BrokerStatus:
        """Get the current connection status."""
        return self._status
    
    @property
    def is_connected(self) -> bool:
        """Check if broker is connected."""
        return self._status == BrokerStatus.CONNECTED
    
    @property
    def active_scripts(self) -> List[Script]:
        """Get the list of active scripts."""
        return self._active_scripts.copy()
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with the broker.
        
        Args:
            credentials: Dictionary containing authentication credentials
                        (api_key, api_secret, client_id, etc.)
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the broker.
        
        Returns:
            True if disconnection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_script_list(self, exchange: Optional[str] = None) -> List[Script]:
        """
        Get list of available scripts/instruments.
        
        Args:
            exchange: Optional exchange name to filter scripts (NSE, BSE, NFO, etc.)
        
        Returns:
            List of Script objects
        """
        pass
    
    @abstractmethod
    def search_scripts(self, query: str, exchange: Optional[str] = None) -> List[Script]:
        """
        Search for scripts by name or symbol.
        
        Args:
            query: Search query string
            exchange: Optional exchange name to filter results
        
        Returns:
            List of matching Script objects
        """
        pass
    
    @abstractmethod
    def get_ltp(self, symbol: str, exchange: str) -> Optional[LTPData]:
        """
        Get Last Traded Price for a script.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange name
        
        Returns:
            LTPData object if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def get_ltp_bulk(self, scripts: List[tuple]) -> Dict[str, LTPData]:
        """
        Get Last Traded Price for multiple scripts.
        
        Args:
            scripts: List of (symbol, exchange) tuples
        
        Returns:
            Dictionary mapping symbol to LTPData
        """
        pass
    
    @abstractmethod
    def add_active_script(self, symbol: str, exchange: str) -> bool:
        """
        Add a script to the active scripts list for monitoring.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange name
        
        Returns:
            True if successfully added, False otherwise
        """
        pass
    
    @abstractmethod
    def remove_active_script(self, symbol: str, exchange: str) -> bool:
        """
        Remove a script from the active scripts list.
        
        Args:
            symbol: Trading symbol
            exchange: Exchange name
        
        Returns:
            True if successfully removed, False otherwise
        """
        pass
    
    def clear_active_scripts(self) -> None:
        """Clear all active scripts."""
        self._active_scripts.clear()
    
    @abstractmethod
    def subscribe_live_data(self, callback) -> bool:
        """
        Subscribe to live market data feed.
        
        Args:
            callback: Function to call when new data arrives
        
        Returns:
            True if subscription successful, False otherwise
        """
        pass
    
    @abstractmethod
    def unsubscribe_live_data(self) -> bool:
        """
        Unsubscribe from live market data feed.
        
        Returns:
            True if unsubscription successful, False otherwise
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of the broker."""
        return f"{self.__class__.__name__}(broker_name='{self._broker_name}', status={self._status.value})"
