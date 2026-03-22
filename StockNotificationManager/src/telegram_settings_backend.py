"""
Telegram Settings Backend Module

Provides a Qt backend for managing Telegram messenger settings with
non-blocking operations using QRunnable and QThreadPool.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging
import json
import requests
import time

from PySide6.QtCore import QObject, Signal, Slot, QRunnable, QThreadPool

from src.settings_manager import SettingsManager
from src.messenger_manager import MessengerManager, MessengerType
from src.messenger_base import MessageType

logger = logging.getLogger(__name__)


class TelegramSettingsTask(QRunnable):
    """Runnable task for Telegram settings operations."""
    
    def __init__(self, operation: str, settings_manager: SettingsManager, 
                 settings_loaded_signal: Signal = None,
                 settings_saved_signal: Signal = None,
                 groups_fetched_signal: Signal = None,
                 message_sent_signal: Signal = None,
                 chat_id_fetched_signal: Signal = None,
                 data: Dict[str, Any] = None):
        super().__init__()
        self.operation = operation
        self.settings_manager = settings_manager
        self.settings_loaded = settings_loaded_signal
        self.settings_saved = settings_saved_signal
        self.groups_fetched = groups_fetched_signal
        self.message_sent = message_sent_signal
        self.chat_id_fetched = chat_id_fetched_signal
        self.data = data or {}
        
    def run(self):
        """Execute the task based on operation type."""
        try:
            if self.operation == "load":
                self._load_settings()
            elif self.operation == "save":
                self._save_settings()
            elif self.operation == "fetch_groups":
                self._fetch_groups()
            elif self.operation == "send_message":
                self._send_test_message()
            elif self.operation == "fetch_chat_id":
                self._fetch_chat_id()
        except Exception as e:
            logger.error(f"Error in TelegramSettingsTask ({self.operation}): {e}", exc_info=True)
            self._emit_error(str(e))
    
    def _load_settings(self):
        """Load settings from settings manager."""
        try:
            settings = self.settings_manager.get_settings()
            # Convert to JSON string for Qt compatibility
            settings_json = json.dumps(settings)
            # Emit signal directly
            if self.settings_loaded:
                self.settings_loaded.emit(settings_json)
        except Exception as e:
            logger.error(f"Failed to load settings: {e}")
            self._emit_error(f"Failed to load settings: {e}")
    
    def _save_settings(self):
        """Save settings to settings manager."""
        try:
            # Update settings with provided data
            self.settings_manager.set_settings(self.data)
            
            # Emit success signal directly
            if self.settings_saved:
                self.settings_saved.emit(True, "Settings saved successfully!")
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            if self.settings_saved:
                self.settings_saved.emit(False, f"Failed to save: {str(e)}")
    
    def _fetch_groups(self):
        """Fetch Telegram groups using chat IDs from settings."""
        try:
            # Get current settings
            settings = self.settings_manager.get_settings()
            
            # Validate bot token
            bot_token = settings.get('bot_token', '').strip()
            
            if not bot_token:
                if self.groups_fetched:
                    self.groups_fetched.emit("[]", False, "Bot token is required")
                return
            
            # Get chat IDs from both fields
            stock_chat_id = settings.get('stock_notification_chat_id', '').strip()
            threshold_chat_id = settings.get('threshold_notification_chat_id', '').strip()
            
            chat_ids = []
            if stock_chat_id:
                chat_ids.append(stock_chat_id)
            if threshold_chat_id and threshold_chat_id != stock_chat_id:
                chat_ids.append(threshold_chat_id)
            
            if not chat_ids:
                if self.groups_fetched:
                    self.groups_fetched.emit("[]", False, "No chat IDs configured")
                return
            
            # Create messenger and authenticate
            msg_manager = MessengerManager()
            credentials = {'bot_token': bot_token}
            success = msg_manager.set_active_messenger(MessengerType.TELEGRAM, credentials)
            
            if not success:
                if self.groups_fetched:
                    self.groups_fetched.emit("[]", False, "Failed to authenticate with Telegram")
                return
            
            # Fetch group info for each chat ID
            groups = []
            
            for chat_id in chat_ids:
                try:
                    # Add group info
                    group_name = "Stock Notifications" if chat_id == stock_chat_id else "Threshold Notifications"
                    if chat_id == stock_chat_id and chat_id == threshold_chat_id:
                        group_name = "Stock & Threshold Notifications"
                    
                    groups.append({
                        "chat_id": str(chat_id),
                        "name": f"{group_name} ({chat_id})"
                    })
                except Exception as e:
                    logger.error(f"Error fetching info for chat {chat_id}: {e}")
            
            if groups:
                groups_json = json.dumps(groups)
                if self.groups_fetched:
                    self.groups_fetched.emit(groups_json, True, f"Found {len(groups)} group(s)")
            else:
                if self.groups_fetched:
                    self.groups_fetched.emit("[]", False, "No groups found")
                
        except Exception as e:
            logger.error(f"Failed to fetch groups: {e}")
            if self.groups_fetched:
                self.groups_fetched.emit("[]", False, f"Error: {str(e)}")
    
    def _send_test_message(self):
        """Send a test message to selected group."""
        try:
            # Get current settings
            settings = self.settings_manager.get_settings()
            
            # Validate bot token
            bot_token = settings.get('bot_token', '').strip()
            
            if not bot_token:
                if self.message_sent:
                    self.message_sent.emit(False, "Bot token is required")
                return
            
            # Get message and chat ID from data
            message = self.data.get('message', '').strip()
            chat_id = self.data.get('chat_id', '').strip()
            
            if not message:
                if self.message_sent:
                    self.message_sent.emit(False, "Message cannot be empty")
                return
            
            if not chat_id:
                if self.message_sent:
                    self.message_sent.emit(False, "Please select a group")
                return
            
            # Create messenger and authenticate
            msg_manager = MessengerManager()
            credentials = {'bot_token': bot_token}
            success = msg_manager.set_active_messenger(MessengerType.TELEGRAM, credentials)
            
            if not success:
                if self.message_sent:
                    self.message_sent.emit(False, "Failed to authenticate with Telegram")
                return
            
            # Send message
            telegram = msg_manager.get_messenger(MessengerType.TELEGRAM)
            receipt = telegram.send_message_to_group(chat_id, message, MessageType.TEXT)
            
            if receipt and getattr(receipt, 'status', '') == 'sent':
                if self.message_sent:
                    self.message_sent.emit(True, "✓ Message sent successfully!")
            else:
                error_msg = getattr(receipt, 'error', 'Unknown error') if receipt else 'No response from server'
                if self.message_sent:
                    self.message_sent.emit(False, f"✗ Failed to send message: {error_msg}")
                
        except Exception as e:
            logger.error(f"Failed to send test message: {e}")
            if self.message_sent:
                self.message_sent.emit(False, f"✗ Error: {str(e)}")
    
    def _fetch_chat_id(self):
        """Fetch multiple chat IDs by polling Telegram getUpdates."""
        try:
            # Get bot token from settings
            settings = self.settings_manager.get_settings()
            bot_token = settings.get('bot_token', '').strip()
            
            if not bot_token:
                if self.chat_id_fetched:
                    self.chat_id_fetched.emit("[]", False, "Bot token is required")
                return
            
            # Get updates
            url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
            
            if self.chat_id_fetched:
                self.chat_id_fetched.emit("[]", False, "Waiting for messages... Send messages to the bot in your groups now (30 seconds).")
            
            # Poll for updates and collect all unique chats (timeout after 30 seconds)
            start_time = time.time()
            last_offset = None
            seen_update_ids = set()
            found_chats = {}  # Dictionary to store unique chats by ID
            
            while time.time() - start_time < 30:
                try:
                    params = {}
                    if last_offset is not None:
                        params['offset'] = last_offset
                    
                    resp = requests.get(url, params=params, timeout=5)
                    resp.raise_for_status()
                    result = resp.json()
                    
                    if not result.get('ok'):
                        if self.chat_id_fetched:
                            self.chat_id_fetched.emit("[]", False, f"Telegram API error: {result.get('description', 'Unknown error')}")
                        return
                    
                    updates = result.get('result', [])
                    
                    for u in updates:
                        uid = u.get('update_id')
                        if uid in seen_update_ids:
                            continue
                        seen_update_ids.add(uid)
                        
                        # Update offset
                        if last_offset is None or uid >= (last_offset or 0):
                            last_offset = uid + 1
                        
                        # Get message
                        msg = u.get('message') or u.get('edited_message') or u.get('channel_post') or u.get('edited_channel_post')
                        if not msg:
                            continue
                        
                        chat = msg.get('chat', {})
                        chat_id = chat.get('id')
                        chat_title = chat.get('title', chat.get('first_name', 'Unknown'))
                        chat_type = chat.get('type', 'unknown')
                        
                        if chat_id and chat_id not in found_chats:
                            found_chats[chat_id] = {
                                'chat_id': str(chat_id),
                                'title': chat_title,
                                'type': chat_type
                            }
                            logger.info(f"Found chat: {chat_title} (ID: {chat_id}, Type: {chat_type})")
                    
                    time.sleep(1)  # Wait 1 second before next poll
                    
                except requests.RequestException as e:
                    logger.error(f"Request error while fetching chat IDs: {e}")
                    time.sleep(1)
                    continue
            
            # Return all found chats
            if found_chats:
                chats_list = list(found_chats.values())
                chats_json = json.dumps(chats_list)
                message = f"Found {len(chats_list)} chat(s). Click on a chat to assign it to a field."
                if self.chat_id_fetched:
                    self.chat_id_fetched.emit(chats_json, True, message)
            else:
                # Timeout with no chats found
                if self.chat_id_fetched:
                    self.chat_id_fetched.emit("[]", False, "No messages received in 30 seconds. Please send messages to your groups and try again.")
                
        except Exception as e:
            logger.error(f"Failed to fetch chat IDs: {e}")
            if self.chat_id_fetched:
                self.chat_id_fetched.emit("[]", False, f"✗ Error: {str(e)}")
    
    def _emit_error(self, message: str):
        """Emit error signal."""
        if self.settings_saved:
            self.settings_saved.emit(False, message)


class TelegramSettingsBackend(QObject):
    """
    Backend for Telegram Settings screen.
    
    Provides non-blocking settings operations using QThreadPool.
    """
    
    # Signals for QML
    settingsLoaded = Signal(str)  # JSON string
    settingsSaved = Signal(bool, str)  # success, message
    groupsFetched = Signal(str, bool, str)  # groups JSON, success, message
    messageSent = Signal(bool, str)  # success, message
    chatIdFetched = Signal(str, bool, str)  # chat_id, success, message
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.thread_pool = QThreadPool.globalInstance()
        logger.info("TelegramSettingsBackend initialized")
    
    @Slot()
    def loadSettings(self):
        """Load Telegram settings (async)."""
        logger.info("Loading Telegram settings...")
        task = TelegramSettingsTask(
            "load", 
            self.settings_manager,
            settings_loaded_signal=self.settingsLoaded
        )
        self.thread_pool.start(task)
    
    @Slot(dict)
    def saveSettings(self, settings: Dict[str, Any]):
        """Save Telegram settings (async)."""
        logger.info("Saving Telegram settings...")
        task = TelegramSettingsTask(
            "save", 
            self.settings_manager,
            settings_saved_signal=self.settingsSaved,
            data=settings
        )
        self.thread_pool.start(task)
    
    @Slot()
    def fetchGroups(self):
        """Fetch Telegram groups (async)."""
        logger.info("Fetching Telegram groups...")
        task = TelegramSettingsTask(
            "fetch_groups", 
            self.settings_manager,
            groups_fetched_signal=self.groupsFetched
        )
        self.thread_pool.start(task)
    
    @Slot(str, str)
    def sendTestMessage(self, chat_id: str, message: str):
        """Send test message to Telegram group (async)."""
        logger.info(f"Sending test message to chat {chat_id}...")
        task = TelegramSettingsTask(
            "send_message", 
            self.settings_manager,
            message_sent_signal=self.messageSent,
            data={'chat_id': chat_id, 'message': message}
        )
        self.thread_pool.start(task)
    
    @Slot()
    def fetchChatId(self):
        """Fetch chat ID by polling Telegram updates (async)."""
        logger.info("Fetching chat ID from Telegram updates...")
        task = TelegramSettingsTask(
            "fetch_chat_id",
            self.settings_manager,
            chat_id_fetched_signal=self.chatIdFetched
        )
        self.thread_pool.start(task)


__all__ = ["TelegramSettingsBackend"]
