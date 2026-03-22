"""
Telegram Messenger Implementation
"""

import logging
import inspect
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
from .messenger_base import MessengerBase, MessengerStatus, MessageType, MessageReceipt

try:
    # Try importing python-telegram-bot
    import telegram
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    logging.warning("python-telegram-bot not installed. Install with: pip install python-telegram-bot")

try:
    import requests
    REQUESTS_AVAILABLE = True
except Exception:
    requests = None
    REQUESTS_AVAILABLE = False

logger = logging.getLogger(__name__)


class TelegramMessenger(MessengerBase):
    """
    Telegram messenger implementation using python-telegram-bot.
    
    Requires:
    - Telegram Bot Token (from @BotFather)
    - Bot must be added to groups/channels to send messages
    """
    
    def __init__(self):
        """Initialize Telegram messenger."""
        super().__init__("Telegram")
        self._bot: Optional[Bot] = None
        self._bot_token: Optional[str] = None

    def _run_bot_call(self, func, *args, **kwargs):
        """Call a Bot method and handle coroutine vs sync results."""
        try:
            result = func(*args, **kwargs)
            if inspect.isawaitable(result):
                try:
                    return asyncio.run(result)
                except RuntimeError:
                    # If the default loop is closed or already running, create a new loop
                    loop = asyncio.new_event_loop()
                    try:
                        asyncio.set_event_loop(loop)
                        return loop.run_until_complete(result)
                    finally:
                        try:
                            asyncio.set_event_loop(None)
                        except Exception:
                            pass
                        loop.close()
            return result
        except Exception:
            # re-raise for caller to handle/log
            raise

    def _send_via_http(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Send HTTP request to Telegram Bot API and return parsed JSON result."""
        if not REQUESTS_AVAILABLE or not self._bot_token:
            raise RuntimeError("HTTP requests not available or bot token missing")

        url = f"https://api.telegram.org/bot{self._bot_token}/{method}"
        resp = requests.post(url, json=payload, timeout=15)
        try:
            data = resp.json()
        except Exception:
            resp.raise_for_status()
            raise

        if not data.get('ok'):
            # raise with text for logging
            raise RuntimeError(f"Telegram API error: {data}")

        return data.get('result')
    
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with Telegram.
        
        Args:
            credentials: Dictionary containing:
                - bot_token: Telegram Bot Token from @BotFather
        
        Returns:
            True if authentication successful
        """
        if not TELEGRAM_AVAILABLE:
            logger.error("python-telegram-bot library not available")
            self._status = MessengerStatus.ERROR
            return False
        
        try:
            self._status = MessengerStatus.CONNECTING
            
            # Get bot token
            self._bot_token = credentials.get('bot_token')
            
            if not self._bot_token:
                logger.error("Missing bot_token in credentials")
                self._status = MessengerStatus.ERROR
                return False
            
            # Initialize bot
            self._bot = Bot(token=self._bot_token)

            # Verify bot token by getting bot info (handle async/sync API)
            bot_info = self._run_bot_call(self._bot.get_me)

            logger.info(f"Telegram bot authenticated: @{getattr(bot_info, 'username', '')}")
            logger.info(f"Bot name: {getattr(bot_info, 'first_name', '')}")
            self._status = MessengerStatus.CONNECTED
            self._credentials = credentials
            return True
            
        except Exception as e:
            logger.error(f"Telegram authentication failed: {e}")
            self._status = MessengerStatus.ERROR
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Telegram."""
        try:
            self._bot = None
            self._bot_token = None
            self._status = MessengerStatus.DISCONNECTED
            logger.info("Telegram disconnected")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting Telegram: {e}")
            return False
    
    def send_message_to_number(self, phone_number: str, message: str,
                               message_type: MessageType = MessageType.TEXT,
                               media_path: Optional[str] = None) -> Optional[MessageReceipt]:
        """
        Send a message to a Telegram user.
        
        Note: For Telegram, you need the user's chat_id, not phone number.
        The phone_number parameter is treated as chat_id for consistency.
        
        Args:
            phone_number: Telegram chat_id (user ID) as string
            message: Message text to send
            message_type: Type of message (TEXT, IMAGE, DOCUMENT, etc.)
            media_path: Path to media file
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        if not self.is_connected or not self._bot:
            logger.error("Not connected to Telegram")
            return None
        
        try:
            chat_id = phone_number  # Treat as chat_id
            logger.info(f"Sending Telegram message to chat_id: {chat_id}")
            
            sent_message = None
            
            if message_type == MessageType.TEXT:
                # Prefer HTTP API if available (matches required payload)
                if REQUESTS_AVAILABLE and self._bot_token:
                    payload = {
                        "chat_id": str(chat_id),
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                    result = self._send_via_http('sendMessage', payload)
                    # result contains message object
                    sent_message = result
                else:
                    sent_message = self._run_bot_call(
                        self._bot.send_message,
                        chat_id=chat_id,
                        text=message,
                        parse_mode='HTML'
                    )
            
            elif message_type == MessageType.IMAGE and media_path:
                # file uploads via HTTP are more complex; fallback to library
                with open(media_path, 'rb') as photo:
                    sent_message = self._run_bot_call(
                        self._bot.send_photo,
                        chat_id=chat_id,
                        photo=photo,
                        caption=message
                    )
            
            elif message_type == MessageType.DOCUMENT and media_path:
                with open(media_path, 'rb') as document:
                    sent_message = self._run_bot_call(
                        self._bot.send_document,
                        chat_id=chat_id,
                        document=document,
                        caption=message
                    )
            
            elif message_type == MessageType.VIDEO and media_path:
                with open(media_path, 'rb') as video:
                    sent_message = self._run_bot_call(
                        self._bot.send_video,
                        chat_id=chat_id,
                        video=video,
                        caption=message
                    )
            
            elif message_type == MessageType.AUDIO and media_path:
                with open(media_path, 'rb') as audio:
                    sent_message = self._run_bot_call(
                        self._bot.send_audio,
                        chat_id=chat_id,
                        audio=audio,
                        caption=message
                    )
            
            if sent_message:
                logger.info(f"✓ Telegram message sent to {chat_id}")

                # sent_message may be a dict (HTTP result) or a Message object
                if isinstance(sent_message, dict):
                    mid = sent_message.get('message_id')
                    mdate = sent_message.get('date')
                    ts = datetime.fromtimestamp(mdate).isoformat() if mdate else datetime.now().isoformat()
                    return MessageReceipt(
                        message_id=str(mid),
                        timestamp=ts,
                        status="sent",
                        recipient=chat_id,
                        message_type=message_type
                    )
                else:
                    return MessageReceipt(
                        message_id=str(sent_message.message_id),
                        timestamp=sent_message.date.isoformat(),
                        status="sent",
                        recipient=chat_id,
                        message_type=message_type
                    )
            else:
                raise Exception("Failed to send message")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return MessageReceipt(
                message_id=f"tg_{datetime.now().timestamp()}",
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
        Send a message to a Telegram group.
        
        Args:
            group_id: Telegram group chat_id (starts with -)
            message: Message text to send
            message_type: Type of message
            media_path: Path to media file
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        if not self.is_connected or not self._bot:
            logger.error("Not connected to Telegram")
            return None
        
        try:
            logger.info(f"Sending Telegram group message to {group_id}")
            
            sent_message = None
            
            if message_type == MessageType.TEXT:
                # Prefer HTTP API if available (matches required payload)
                if REQUESTS_AVAILABLE and self._bot_token:
                    payload = {
                        "chat_id": str(group_id),
                        "text": message,
                        "parse_mode": "Markdown"
                    }
                    result = self._send_via_http('sendMessage', payload)
                    sent_message = result
                else:
                    sent_message = self._run_bot_call(
                        self._bot.send_message,
                        chat_id=group_id,
                        text=message,
                        parse_mode='HTML'
                    )
            
            elif message_type == MessageType.IMAGE and media_path:
                with open(media_path, 'rb') as photo:
                    sent_message = self._run_bot_call(
                        self._bot.send_photo,
                        chat_id=group_id,
                        photo=photo,
                        caption=message
                    )
            
            elif message_type == MessageType.DOCUMENT and media_path:
                with open(media_path, 'rb') as document:
                    sent_message = self._run_bot_call(
                        self._bot.send_document,
                        chat_id=group_id,
                        document=document,
                        caption=message
                    )
            
            if sent_message:
                logger.info(f"✓ Telegram group message sent to {group_id}")
                # sent_message may be dict (HTTP) or Message object
                if isinstance(sent_message, dict):
                    mid = sent_message.get('message_id')
                    mdate = sent_message.get('date')
                    ts = datetime.fromtimestamp(mdate).isoformat() if mdate else datetime.now().isoformat()
                    return MessageReceipt(
                        message_id=str(mid),
                        timestamp=ts,
                        status="sent",
                        recipient=group_id,
                        message_type=message_type
                    )
                else:
                    return MessageReceipt(
                        message_id=str(sent_message.message_id),
                        timestamp=sent_message.date.isoformat(),
                        status="sent",
                        recipient=group_id,
                        message_type=message_type
                    )
            else:
                raise Exception("Failed to send group message")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram group message: {e}")
            return MessageReceipt(
                message_id=f"tg_group_{datetime.now().timestamp()}",
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
        Send a message to a Telegram channel.
        
        Note: Bot must be an admin of the channel to post.
        
        Args:
            channel_id: Telegram channel username (@channel) or channel_id
            message: Message text to send
            message_type: Type of message
            media_path: Path to media file
        
        Returns:
            MessageReceipt if successful, None otherwise
        """
        if not self.is_connected or not self._bot:
            logger.error("Not connected to Telegram")
            return None
        
        try:
            logger.info(f"Sending Telegram channel message to {channel_id}")
            
            sent_message = None
            
            if message_type == MessageType.TEXT:
                sent_message = self._bot.send_message(
                    chat_id=channel_id,
                    text=message,
                    parse_mode='HTML'
                )
            
            elif message_type == MessageType.IMAGE and media_path:
                with open(media_path, 'rb') as photo:
                    sent_message = self._bot.send_photo(
                        chat_id=channel_id,
                        photo=photo,
                        caption=message
                    )
            
            elif message_type == MessageType.DOCUMENT and media_path:
                with open(media_path, 'rb') as document:
                    sent_message = self._bot.send_document(
                        chat_id=channel_id,
                        document=document,
                        caption=message
                    )
            
            if sent_message:
                logger.info(f"✓ Telegram channel message sent to {channel_id}")
                
                return MessageReceipt(
                    message_id=str(sent_message.message_id),
                    timestamp=sent_message.date.isoformat(),
                    status="sent",
                    recipient=channel_id,
                    message_type=message_type
                )
            else:
                raise Exception("Failed to send channel message")
            
        except Exception as e:
            logger.error(f"Failed to send Telegram channel message: {e}")
            return MessageReceipt(
                message_id=f"tg_channel_{datetime.now().timestamp()}",
                timestamp=datetime.now().isoformat(),
                status="failed",
                recipient=channel_id,
                message_type=message_type,
                error=str(e)
            )
    
    def get_groups(self) -> List[Dict[str, str]]:
        """
        Get list of Telegram groups where the bot is a member.
        
        Note: Telegram Bot API doesn't provide a direct method to list groups.
        Groups must be tracked when bot receives messages.
        
        Returns:
            Empty list (requires separate implementation to track groups)
        """
        logger.warning("Getting group list requires tracking bot updates")
        logger.info("Store group IDs when bot receives messages from groups")
        return []
    
    def get_channels(self) -> List[Dict[str, str]]:
        """
        Get list of Telegram channels where the bot is an admin.
        
        Note: Requires tracking or manual configuration.
        
        Returns:
            Empty list (requires manual configuration)
        """
        logger.warning("Getting channel list requires manual configuration")
        logger.info("Store channel IDs/usernames in configuration")
        return []
