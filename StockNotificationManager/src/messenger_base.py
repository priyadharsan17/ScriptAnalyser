"""
Base class for messaging platforms (WhatsApp, Telegram, etc.)
"""

from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MessengerStatus(Enum):
    """Status of messenger connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"


class MessageType(Enum):
    """Type of message to send."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    VIDEO = "video"
    AUDIO = "audio"
    TEMPLATE = "template"


@dataclass
class MessageReceipt:
    """Receipt confirmation for sent message."""
    message_id: str
    timestamp: str
    status: str
    recipient: str
    message_type: MessageType
    error: Optional[str] = None


class MessengerBase(ABC):
    """
    Abstract base class for all messenger implementations.
    All messenger classes must inherit from this and implement the abstract methods.
    """
    
    def __init__(self, messenger_name: str):
        """
        Initialize the messenger.
        
        Args:
            messenger_name: Name of the messenger (e.g., "WhatsApp", "Telegram")
        """
        self.messenger_name = messenger_name
        self._status = MessengerStatus.DISCONNECTED
        self._credentials: Dict[str, Any] = {}
    
    @property
    def status(self) -> MessengerStatus:
        """Get current messenger status."""
        return self._status
    
    @property
    def is_connected(self) -> bool:
        """Check if messenger is connected."""
        return self._status == MessengerStatus.CONNECTED
    
    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with the messenger service.
        
        Args:
            credentials: Dictionary containing authentication credentials
                        (e.g., API keys, tokens, phone numbers, etc.)
        
        Returns:
            True if authentication successful, False otherwise
        """
        pass
    
    @abstractmethod
    def disconnect(self) -> bool:
        """
        Disconnect from the messenger service.
        
        Returns:
            True if disconnection successful
        """
        pass
    
    @abstractmethod
    def send_message_to_number(self, phone_number: str, message: str, 
                               message_type: MessageType = MessageType.TEXT,
                               media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a phone number.
        
        Args:
            phone_number: Recipient phone number (with country code)
            message: Message text to send
            message_type: Type of message (text, image, etc.)
            media_path: Path to media file (for non-text messages)
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def send_message_to_group(self, group_id: str, message: str,
                             message_type: MessageType = MessageType.TEXT,
                             media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a group.
        
        Args:
            group_id: Group identifier
            message: Message text to send
            message_type: Type of message (text, image, etc.)
            media_path: Path to media file (for non-text messages)
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def send_message_to_channel(self, channel_id: str, message: str,
                                message_type: MessageType = MessageType.TEXT,
                                media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a channel.
        
        Args:
            channel_id: Channel identifier
            message: Message text to send
            message_type: Type of message (text, image, etc.)
            media_path: Path to media file (for non-text messages)
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        pass
    
    @abstractmethod
    def get_groups(self) -> List[Dict[str, str]]:
        """
        Get list of available groups.
        
        Returns:
            List of dictionaries containing group info (id, name, etc.)
        """
        pass
    
    @abstractmethod
    def get_channels(self) -> List[Dict[str, str]]:
        """
        Get list of available channels.
        
        Returns:
            List of dictionaries containing channel info (id, name, etc.)
        """
        pass
    
    def __repr__(self) -> str:
        """String representation."""
        return f"{self.messenger_name} Messenger (Status: {self._status.value})"
