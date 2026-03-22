"""
WhatsApp Messenger Implementation
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from .messenger_base import MessengerBase, MessengerStatus, MessageType, MessageReceipt

try:
    # Try importing pywhatkit for WhatsApp functionality
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    logging.warning("pywhatkit not installed. Install with: pip install pywhatkit")

logger = logging.getLogger(__name__)


class WhatsAppMessenger(MessengerBase):
    """
    WhatsApp messenger implementation using pywhatkit.
    
    Note: pywhatkit uses WhatsApp Web, which requires:
    - WhatsApp installed on the computer
    - QR code scanning for authentication
    - Browser automation (opens WhatsApp Web)
    """
    
    def __init__(self):
        """Initialize WhatsApp messenger."""
        super().__init__("WhatsApp")
        self._tab_close = True
        self._wait_time = 15  # Seconds to wait before sending
        self._close_time = 2   # Seconds to wait after sending
    
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with WhatsApp.
        
        For pywhatkit, authentication happens automatically via WhatsApp Web.
        This method validates that the library is available.
        
        Args:
            credentials: Dictionary (not used for pywhatkit, but kept for interface consistency)
        
        Returns:
            True if pywhatkit is available
        """
        if not PYWHATKIT_AVAILABLE:
            logger.error("pywhatkit library not available")
            self._status = MessengerStatus.ERROR
            return False

        # Idempotent: if already connected, return True
        if self._status == MessengerStatus.CONNECTED:
            logger.info("WhatsApp already authenticated")
            return True

        try:
            self._status = MessengerStatus.CONNECTING

            # Store optional settings
            self._tab_close = credentials.get('tab_close', True)
            self._wait_time = credentials.get('wait_time', 15)
            self._close_time = credentials.get('close_time', 2)

            logger.info("WhatsApp messenger initialized (uses WhatsApp Web)")
            logger.info("Make sure WhatsApp Web is logged in on your default browser")
            self._status = MessengerStatus.CONNECTED
            self._credentials = credentials
            return True

        except Exception as e:
            logger.error(f"WhatsApp authentication failed: {e}")
            self._status = MessengerStatus.ERROR
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from WhatsApp (no-op for pywhatkit)."""
        try:
            self._status = MessengerStatus.DISCONNECTED
            logger.info("WhatsApp disconnected")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting WhatsApp: {e}")
            return False
    
    def send_message_to_number(self, phone_number: str, message: str,
                               message_type: MessageType = MessageType.TEXT,
                               media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a phone number via WhatsApp.
        
        Args:
            phone_number: Phone number with country code (e.g., "+919876543210")
            message: Message text to send
            message_type: Type of message (currently only TEXT supported by pywhatkit)
            media_path: Path to media file (for image messages)
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        if not self.is_connected or not PYWHATKIT_AVAILABLE:
            logger.error("Not connected to WhatsApp")
            return None
        
        try:
            logger.info(f"Sending WhatsApp message to {phone_number}")
            
            if message_type == MessageType.IMAGE and media_path:
                # Send image with caption
                pywhatkit.sendwhats_image(
                    phone_number,
                    media_path,
                    message,
                    wait_time=self._wait_time,
                    tab_close=self._tab_close,
                    close_time=self._close_time
                )
            else:
                # Send text message instantly
                pywhatkit.sendwhatmsg_instantly(
                    phone_number,
                    message,
                    wait_time=self._wait_time,
                    tab_close=self._tab_close,
                    close_time=self._close_time
                )
            
            logger.info(f"✓ WhatsApp message sent to {phone_number}")
            
            return MessageReceipt(
                message_id=f"wa_{datetime.now().timestamp()}",
                timestamp=datetime.now().isoformat(),
                status="sent",
                recipient=phone_number,
                message_type=message_type
            )
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp message to {phone_number}: {e}")
            return MessageReceipt(
                message_id=f"wa_{datetime.now().timestamp()}",
                timestamp=datetime.now().isoformat(),
                status="failed",
                recipient=phone_number,
                message_type=message_type,
                error=str(e)
            )
    
    def send_message_to_group(self, group_id: str, message: str,
                             message_type: MessageType = MessageType.TEXT,
                             media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a WhatsApp group.
        
        Args:
            group_id: Group ID (WhatsApp group invite link or group JID)
            message: Message text to send
            message_type: Type of message
            media_path: Path to media file
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        if not self.is_connected or not PYWHATKIT_AVAILABLE:
            logger.error("Not connected to WhatsApp")
            return None
        
        try:
            logger.info(f"Sending WhatsApp group message to {group_id}")
            
            # pywhatkit group messaging
            pywhatkit.sendwhatmsg_to_group_instantly(
                group_id,
                message,
                wait_time=self._wait_time,
                tab_close=self._tab_close,
                close_time=self._close_time
            )
            
            logger.info(f"✓ WhatsApp group message sent to {group_id}")
            
            return MessageReceipt(
                message_id=f"wa_group_{datetime.now().timestamp()}",
                timestamp=datetime.now().isoformat(),
                status="sent",
                recipient=group_id,
                message_type=message_type
            )
            
        except Exception as e:
            logger.error(f"Failed to send WhatsApp group message: {e}")
            return MessageReceipt(
                message_id=f"wa_group_{datetime.now().timestamp()}",
                timestamp=datetime.now().isoformat(),
                status="failed",
                recipient=group_id,
                message_type=message_type,
                error=str(e)
            )
    
    def send_message_to_channel(self, channel_id: str, message: str,
                                message_type: MessageType = MessageType.TEXT,
                                media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a WhatsApp channel.
        
        Note: WhatsApp channels are relatively new and may not be fully supported
        by pywhatkit. This method is a placeholder for future implementation.
        
        Args:
            channel_id: Channel identifier
            message: Message text to send
            message_type: Type of message
            media_path: Path to media file
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        logger.warning("WhatsApp channels not yet supported by pywhatkit")
        logger.info("Consider using WhatsApp Business API for channel support")
        
        return MessageReceipt(
            message_id=f"wa_channel_{datetime.now().timestamp()}",
            timestamp=datetime.now().isoformat(),
            status="not_supported",
            recipient=channel_id,
            message_type=message_type,
            error="WhatsApp channels not supported by current implementation"
        )
    
    def get_groups(self) -> List[Dict[str, str]]:
        """
        Get list of WhatsApp groups.
        
        Note: pywhatkit doesn't provide group listing functionality.
        You need to manually get group IDs from WhatsApp Web.
        
        Returns:
            Empty list (not supported by pywhatkit)
        """
        logger.warning("Getting group list not supported by pywhatkit")
        logger.info("Manually obtain group IDs from WhatsApp Web")
        return []
    
    def get_channels(self) -> List[Dict[str, str]]:
        """
        Get list of WhatsApp channels.
        
        Note: Not supported by pywhatkit.
        
        Returns:
            Empty list
        """
        logger.warning("Getting channel list not supported by pywhatkit")
        return []
