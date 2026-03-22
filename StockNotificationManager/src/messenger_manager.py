"""
Messenger Manager - Factory and lifecycle manager for messengers
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any
from .messenger_base import MessengerBase
from .whatsapp_messenger import WhatsAppMessenger
from .telegram_messenger import TelegramMessenger

logger = logging.getLogger(__name__)


class MessengerType(Enum):
    """Supported messenger types."""
    WHATSAPP = "whatsapp"
    TELEGRAM = "telegram"


class MessengerManager:
    """
    Manager for messenger instances.
    Handles creation, authentication, and lifecycle of messengers.
    """
    
    def __init__(self):
        """Initialize messenger manager."""
        self._active_messenger: Optional[MessengerBase] = None
        self._messenger_instances: Dict[MessengerType, MessengerBase] = {}
    
    @property
    def active_messenger(self) -> Optional[MessengerBase]:
        """Get the currently active messenger."""
        return self._active_messenger
    
    def create_messenger(self, messenger_type: MessengerType) -> MessengerBase:
        """
        Create a messenger instance.
        
        Args:
            messenger_type: Type of messenger to create
        
        Returns:
            Messenger instance
        
        Raises:
            ValueError: If messenger type is not supported
        """
        # Check if instance already exists
        if messenger_type in self._messenger_instances:
            logger.info(f"Returning existing {messenger_type.value} messenger instance")
            return self._messenger_instances[messenger_type]
        
        # Create new instance
        if messenger_type == MessengerType.WHATSAPP:
            messenger = WhatsAppMessenger()
            logger.info("Created new whatsapp messenger instance")
        
        elif messenger_type == MessengerType.TELEGRAM:
            messenger = TelegramMessenger()
            logger.info("Created new telegram messenger instance")
        
        else:
            raise ValueError(f"Unsupported messenger type: {messenger_type}")
        
        # Store instance
        self._messenger_instances[messenger_type] = messenger
        return messenger
    
    def set_active_messenger(self, messenger_type: MessengerType, 
                           credentials: Dict[str, Any]) -> bool:
        """
        Set active messenger and authenticate.
        
        Args:
            messenger_type: Type of messenger to activate
            credentials: Authentication credentials
        
        Returns:
            True if successful
        """
        try:
            # Get or create messenger
            messenger = self.create_messenger(messenger_type)
            
            # Authenticate
            if messenger.authenticate(credentials):
                self._active_messenger = messenger
                logger.info(f"Successfully set {messenger_type.value} as active messenger")
                return True
            else:
                logger.error(f"Failed to authenticate {messenger_type.value}")
                return False
        
        except Exception as e:
            logger.error(f"Error setting active messenger: {e}")
            return False
    
    def disconnect_active_messenger(self) -> bool:
        """
        Disconnect the active messenger.
        
        Returns:
            True if successful
        """
        if self._active_messenger:
            success = self._active_messenger.disconnect()
            if success:
                logger.info(f"Disconnected {self._active_messenger.messenger_name}")
                self._active_messenger = None
            return success
        return True
    
    def disconnect_all(self) -> bool:
        """
        Disconnect all messenger instances.
        
        Returns:
            True if all disconnected successfully
        """
        all_success = True
        
        for messenger_type, messenger in self._messenger_instances.items():
            try:
                messenger.disconnect()
                logger.info(f"Disconnected {messenger_type.value}")
            except Exception as e:
                logger.error(f"Error disconnecting {messenger_type.value}: {e}")
                all_success = False
        
        self._messenger_instances.clear()
        self._active_messenger = None
        
        return all_success
    
    def get_messenger(self, messenger_type: MessengerType) -> Optional[MessengerBase]:
        """
        Get a specific messenger instance.
        
        Args:
            messenger_type: Type of messenger to get
        
        Returns:
            Messenger instance if exists, None otherwise
        """
        return self._messenger_instances.get(messenger_type)
    
    def cleanup(self):
        """Cleanup all messenger connections."""
        logger.info("Cleaning up messenger manager")
        self.disconnect_all()
    
    def __del__(self):
        """Destructor to ensure cleanup."""
        self.cleanup()
