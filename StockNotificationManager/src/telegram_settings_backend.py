"""
Telegram Settings Backend Module

Provides a Qt backend for managing Telegram messenger settings with
non-blocking operations using QRunnable and QThreadPool.
"""

from pathlib import Path
from typing import Dict, Any, List
import logging
import json

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
                 data: Dict[str, Any] = None):
        super().__init__()
        self.operation = operation
        self.settings_manager = settings_manager
        self.settings_loaded = settings_loaded_signal
        self.settings_saved = settings_saved_signal
        self.groups_fetched = groups_fetched_signal
        self.message_sent = message_sent_signal
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
            
            # Get chat IDs
            chat_ids = settings.get('chat_ids', [])
            if isinstance(chat_ids, str):
                chat_ids = [chat_ids] if chat_ids else []
            
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
            telegram = msg_manager.get_messenger(MessengerType.TELEGRAM)
            groups = []
            
            for chat_id in chat_ids:
                try:
                    # Try to get chat info (this will work if bot is in the group)
                    # For now, we'll just store the chat ID as the name
                    groups.append({
                        "chat_id": str(chat_id),
                        "name": f"Group {chat_id}"
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


__all__ = ["TelegramSettingsBackend"]
