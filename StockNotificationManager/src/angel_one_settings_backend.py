"""
Angel One Settings Backend Module

Provides a Qt backend for managing Angel One broker settings with
non-blocking operations using QRunnable and QThreadPool.
"""

from pathlib import Path
from typing import Dict, Any
import logging
import json

from PySide6.QtCore import QObject, Signal, Slot, QRunnable, QThreadPool

from src.settings_manager import SettingsManager
from src.broker_manager import BrokerManager, BrokerType

logger = logging.getLogger(__name__)


class AngelOneSettingsTask(QRunnable):
    """Runnable task for Angel One settings operations."""
    
    def __init__(self, operation: str, settings_manager: SettingsManager, 
                 settings_loaded_signal: Signal = None,
                 settings_saved_signal: Signal = None,
                 connection_tested_signal: Signal = None,
                 data: Dict[str, Any] = None):
        super().__init__()
        self.operation = operation
        self.settings_manager = settings_manager
        self.settings_loaded = settings_loaded_signal
        self.settings_saved = settings_saved_signal
        self.connection_tested = connection_tested_signal
        self.data = data or {}
        
    def run(self):
        """Execute the task based on operation type."""
        try:
            if self.operation == "load":
                self._load_settings()
            elif self.operation == "save":
                self._save_settings()
            elif self.operation == "test":
                self._test_connection()
        except Exception as e:
            logger.error(f"Error in AngelOneSettingsTask ({self.operation}): {e}", exc_info=True)
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
    
    def _test_connection(self):
        """Test Angel One connection with current settings."""
        try:
            # Get current settings
            settings = self.settings_manager.get_settings()
            
            # Validate required fields
            api_key = settings.get('api_key', '').strip()
            client_id = settings.get('client_id', '').strip()
            password = settings.get('password', '').strip()
            
            if not all([api_key, client_id, password]):
                if self.connection_tested:
                    self.connection_tested.emit(False, "Missing required credentials (API Key, Client ID, or Password)")
                return
            
            # Prepare credentials
            totp_secret = settings.get('totp_secret', '').strip()
            credentials = {
                'api_key': api_key,
                'client_id': client_id,
                'password': password,
                'totp': totp_secret if totp_secret and totp_secret not in ['', 'optional_totp_secret', 'YOUR_TOTP_SECRET_HERE (optional)'] else None
            }
            
            # Create a temporary broker manager to test
            broker_manager = BrokerManager()
            success = broker_manager.set_active_broker(BrokerType.ANGEL_ONE, credentials)
            
            if success:
                # Disconnect after successful test
                broker_manager.disconnect_active_broker()
                if self.connection_tested:
                    self.connection_tested.emit(True, "✓ Connection successful! Credentials are valid.")
            else:
                if self.connection_tested:
                    self.connection_tested.emit(False, "✗ Connection failed. Please check your credentials.")
                
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            if self.connection_tested:
                self.connection_tested.emit(False, f"✗ Connection test error: {str(e)}")
    
    def _emit_error(self, message: str):
        """Emit error signal."""
        if self.settings_saved:
            self.settings_saved.emit(False, message)


class AngelOneSettingsBackend(QObject):
    """
    Backend for Angel One Settings screen.
    
    Provides non-blocking settings operations using QThreadPool.
    """
    
    # Signals for QML - use string (JSON) for dict compatibility
    settingsLoaded = Signal(str)  # JSON string
    settingsSaved = Signal(bool, str)  # success, message
    connectionTested = Signal(bool, str)  # success, message
    
    def __init__(self, settings_manager: SettingsManager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.thread_pool = QThreadPool.globalInstance()
        logger.info("AngelOneSettingsBackend initialized")
    
    @Slot()
    def loadSettings(self):
        """Load Angel One settings (async)."""
        logger.info("Loading Angel One settings...")
        task = AngelOneSettingsTask(
            "load", 
            self.settings_manager,
            settings_loaded_signal=self.settingsLoaded
        )
        self.thread_pool.start(task)
    
    @Slot(dict)
    def saveSettings(self, settings: Dict[str, Any]):
        """Save Angel One settings (async)."""
        logger.info("Saving Angel One settings...")
        task = AngelOneSettingsTask(
            "save", 
            self.settings_manager,
            settings_saved_signal=self.settingsSaved,
            data=settings
        )
        self.thread_pool.start(task)
    
    @Slot()
    def testConnection(self):
        """Test Angel One connection (async)."""
        logger.info("Testing Angel One connection...")
        task = AngelOneSettingsTask(
            "test", 
            self.settings_manager,
            connection_tested_signal=self.connectionTested
        )
        self.thread_pool.start(task)


__all__ = ["AngelOneSettingsBackend"]
