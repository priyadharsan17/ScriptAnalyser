"""
Broker Manager - Factory class to manage broker instances.
"""

import logging
from typing import Optional, Dict, Any
from enum import Enum
from .broker_base import BrokerBase
from .angel_one_broker import AngelOneBroker
from .motilal_oswal_broker import MotilalOswalBroker


logger = logging.getLogger(__name__)


class BrokerType(Enum):
    """Enumeration of supported brokers."""
    ANGEL_ONE = "angel_one"
    MOTILAL_OSWAL = "motilal_oswal"


class BrokerManager:
    """
    Factory and manager class for broker instances.
    Handles broker creation, configuration, and lifecycle management.
    """
    
    # Registry of broker types to their implementation classes
    _BROKER_REGISTRY = {
        BrokerType.ANGEL_ONE: AngelOneBroker,
        BrokerType.MOTILAL_OSWAL: MotilalOswalBroker,
    }
    
    def __init__(self):
        """Initialize the broker manager."""
        self._active_broker: Optional[BrokerBase] = None
        self._broker_instances: Dict[BrokerType, BrokerBase] = {}
    
    @property
    def active_broker(self) -> Optional[BrokerBase]:
        """Get the currently active broker."""
        return self._active_broker
    
    @property
    def is_connected(self) -> bool:
        """Check if active broker is connected."""
        return self._active_broker is not None and self._active_broker.is_connected
    
    def create_broker(self, broker_type: BrokerType) -> BrokerBase:
        """
        Create a broker instance.
        
        Args:
            broker_type: Type of broker to create
        
        Returns:
            BrokerBase instance
        
        Raises:
            ValueError: If broker type is not supported
        """
        if broker_type not in self._BROKER_REGISTRY:
            raise ValueError(f"Unsupported broker type: {broker_type}")
        
        # Check if instance already exists
        if broker_type in self._broker_instances:
            logger.info(f"Returning existing {broker_type.value} instance")
            return self._broker_instances[broker_type]
        
        # Create new instance
        broker_class = self._BROKER_REGISTRY[broker_type]
        broker = broker_class()
        self._broker_instances[broker_type] = broker
        
        logger.info(f"Created new {broker_type.value} broker instance")
        return broker
    
    def set_active_broker(self, broker_type: BrokerType, credentials: Dict[str, Any]) -> bool:
        """
        Set and authenticate a broker as the active broker.
        
        Args:
            broker_type: Type of broker to activate
            credentials: Authentication credentials
        
        Returns:
            True if successfully authenticated and set as active
        """
        try:
            # Disconnect current broker if exists
            if self._active_broker and self._active_broker.is_connected:
                logger.info(f"Disconnecting current broker: {self._active_broker.broker_name}")
                self._active_broker.disconnect()
            
            # Create or get broker instance
            broker = self.create_broker(broker_type)
            
            # Authenticate
            if broker.authenticate(credentials):
                self._active_broker = broker
                logger.info(f"Successfully set {broker.broker_name} as active broker")
                return True
            else:
                logger.error(f"Failed to authenticate {broker.broker_name}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to set active broker: {e}")
            return False
    
    def disconnect_active_broker(self) -> bool:
        """
        Disconnect the active broker.
        
        Returns:
            True if successfully disconnected
        """
        if not self._active_broker:
            logger.warning("No active broker to disconnect")
            return False
        
        try:
            result = self._active_broker.disconnect()
            if result:
                logger.info(f"Disconnected {self._active_broker.broker_name}")
                self._active_broker = None
            return result
            
        except Exception as e:
            logger.error(f"Failed to disconnect active broker: {e}")
            return False
    
    def get_supported_brokers(self) -> list:
        """
        Get list of supported broker types.
        
        Returns:
            List of BrokerType enums
        """
        return list(self._BROKER_REGISTRY.keys())
    
    def cleanup(self) -> None:
        """Clean up all broker instances."""
        logger.info("Cleaning up broker manager")
        
        # Disconnect all brokers
        for broker_type, broker in self._broker_instances.items():
            if broker.is_connected:
                try:
                    broker.disconnect()
                    logger.info(f"Disconnected {broker.broker_name}")
                except Exception as e:
                    logger.error(f"Error disconnecting {broker.broker_name}: {e}")
        
        # Clear references
        self._active_broker = None
        self._broker_instances.clear()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except:
            pass
