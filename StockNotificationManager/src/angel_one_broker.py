"""
Angel One (Angel Broking) broker implementation.
"""

import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from .broker_base import BrokerBase, BrokerStatus, Script, LTPData

try:
    from SmartApi import SmartConnect
    from SmartApi.smartWebSocketV2 import SmartWebSocketV2
    import pyotp
    SMARTAPI_AVAILABLE = True
except ImportError:
    SMARTAPI_AVAILABLE = False
    logging.warning("SmartApi not installed. Install with: pip install smartapi-python pyotp")


logger = logging.getLogger(__name__)


class AngelOneBroker(BrokerBase):
    """
    Angel One broker implementation.
    Implements the Angel One SmartAPI for trading operations.
    """
    
    def __init__(self):
        """Initialize Angel One broker."""
        super().__init__("Angel One")
        self._smart_api: Optional[SmartConnect] = None
        self._api_key: Optional[str] = None
        self._client_id: Optional[str] = None
        self._password: Optional[str] = None
        self._session_token: Optional[str] = None
        self._feed_token: Optional[str] = None
        self._refresh_token: Optional[str] = None
        self._websocket: Optional[SmartWebSocketV2] = None
        
        if not SMARTAPI_AVAILABLE:
            logger.warning("SmartApi library not available")
        
    def authenticate(self, credentials: Dict[str, Any]) -> bool:
        """
        Authenticate with Angel One.
        
        Args:
            credentials: Dictionary with 'api_key', 'client_id', 'password', 'totp' (optional)
        
        Returns:
            True if authentication successful
        """
        if not SMARTAPI_AVAILABLE:
            logger.error("SmartApi library not available")
            self._status = BrokerStatus.ERROR
            return False
            
        try:
            self._status = BrokerStatus.CONNECTING
            
            # Extract credentials
            self._api_key = credentials.get('api_key')
            self._client_id = credentials.get('client_id')
            self._password = credentials.get('password')
            totp_secret = credentials.get('totp')
            
            if not all([self._api_key, self._client_id, self._password]):
                logger.error("Missing required credentials")
                self._status = BrokerStatus.ERROR
                return False
            
            # Generate TOTP if secret is provided
            totp_code = None
            if totp_secret:
                try:
                    totp_generator = pyotp.TOTP(totp_secret)
                    totp_code = totp_generator.now()
                    logger.info(f"Generated TOTP code from secret")
                except Exception as e:
                    logger.warning(f"Failed to generate TOTP: {e}")
                    logger.warning("Ensure totp_secret is a valid base32 string")
            else:
                logger.warning("No TOTP secret provided - authentication may fail")
                logger.warning("Add 'totp_secret' to your config/angel_config.json")
            
            # Initialize SmartConnect
            self._smart_api = SmartConnect(api_key=self._api_key)
            
            # Generate session
            data = self._smart_api.generateSession(self._client_id, self._password, totp_code)
            
            if data['status']:
                # Get tokens from response
                jwt_token = data['data']['jwtToken']
                
                # Remove "Bearer " prefix if present (SmartAPI adds it automatically)
                if jwt_token.startswith('Bearer '):
                    jwt_token = jwt_token[7:]  # Remove "Bearer " prefix
                
                self._session_token = jwt_token
                self._refresh_token = data['data']['refreshToken']
                self._feed_token = self._smart_api.getfeedToken()
                
                # Set access token - SmartAPI will add "Bearer " prefix automatically
                self._smart_api.setAccessToken(self._session_token)
                
                # Also set the feed token
                self._smart_api.setFeedToken(self._feed_token)
                
                # Verify token was set (debugging)
                logger.debug(f"Token set in SmartAPI: {hasattr(self._smart_api, 'access_token')}")
                if hasattr(self._smart_api, 'access_token'):
                    logger.debug(f"Access token value: {str(self._smart_api.access_token)[:50]}...")
                
                logger.info(f"Angel One authentication successful for client: {self._client_id}")
                logger.info(f"JWT token length: {len(self._session_token)} characters")
                self._status = BrokerStatus.CONNECTED
                self._credentials = credentials
                return True
            else:
                logger.error(f"Angel One authentication failed: {data.get('message', 'Unknown error')}")
                self._status = BrokerStatus.ERROR
                return False
            
        except Exception as e:
            logger.error(f"Angel One authentication failed: {e}")
            self._status = BrokerStatus.ERROR
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from Angel One."""
        try:
            # Unsubscribe from websocket if active
            if self._websocket:
                self.unsubscribe_live_data()
            
            # Terminate session
            if self._smart_api and self._client_id:
                self._smart_api.terminateSession(self._client_id)
            
            self._status = BrokerStatus.DISCONNECTED
            self._session_token = None
            self._feed_token = None
            self._refresh_token = None
            self._smart_api = None
            logger.info("Angel One disconnected")
            return True
            
        except Exception as e:
            logger.error(f"Angel One disconnection failed: {e}")
            return False
    
    def get_script_list(self, exchange: Optional[str] = None) -> List[Script]:
        """
        Get list of available scripts from Angel One.
        
        Args:
            exchange: Optional exchange filter (NSE, BSE, NFO, MCX, etc.)
        
        Returns:
            List of Script objects
        """
        if not self.is_connected or not self._smart_api:
            logger.error("Not connected to Angel One")
            return []
        
        try:
            # Get instrument list
            response = self._smart_api.getAllInstruments()
            
            scripts = []
            if response:
                for instrument in response:
                    # Filter by exchange if specified
                    if exchange and instrument.get('exch_seg') != exchange:
                        continue
                    
                    script = Script(
                        symbol=instrument.get('symbol', ''),
                        token=instrument.get('token', ''),
                        exchange=instrument.get('exch_seg', ''),
                        name=instrument.get('name', instrument.get('symbol', '')),
                        lot_size=int(instrument.get('lotsize', 1)),
                        tick_size=float(instrument.get('tick_size', 0.05))
                    )
                    scripts.append(script)
            
            logger.info(f"Retrieved {len(scripts)} scripts from Angel One")
            return scripts
            
        except Exception as e:
            logger.error(f"Failed to get script list: {e}")
            return []
    
    def search_scripts(self, query: str, exchange: Optional[str] = None) -> List[Script]:
        """Search for scripts by name or symbol."""
        if not self.is_connected or not self._smart_api:
            logger.error("Not connected to Angel One")
            return []
        
        try:
            # Use searchScrip API
            logger.debug(f"Searching for '{query}' on exchange '{exchange or 'NSE'}'")
            response = self._smart_api.searchScrip(exchange or "NSE", query)
            
            logger.debug(f"Search response: {response}")
            
            scripts = []
            # Angel One API can return different response formats
            if response:
                # Check for 'data' key (successful response)
                if isinstance(response, dict) and 'data' in response:
                    data_list = response['data']
                    if isinstance(data_list, list):
                        for instrument in data_list:
                            script = Script(
                                symbol=instrument.get('tradingsymbol', ''),
                                token=instrument.get('symboltoken', ''),
                                exchange=instrument.get('exchange', exchange or 'NSE'),
                                name=instrument.get('name', instrument.get('tradingsymbol', '')),
                                lot_size=int(instrument.get('lotsize', 1)),
                                tick_size=float(instrument.get('tick_size', 0.05))
                            )
                            scripts.append(script)
                # Handle direct list response
                elif isinstance(response, list):
                    for instrument in response:
                        script = Script(
                            symbol=instrument.get('tradingsymbol', ''),
                            token=instrument.get('symboltoken', ''),
                            exchange=instrument.get('exchange', exchange or 'NSE'),
                            name=instrument.get('name', instrument.get('tradingsymbol', '')),
                            lot_size=int(instrument.get('lotsize', 1)),
                            tick_size=float(instrument.get('tick_size', 0.05))
                        )
                        scripts.append(script)
            
            logger.info(f"Found {len(scripts)} scripts matching '{query}'")
            return scripts
            
        except Exception as e:
            logger.error(f"Failed to search scripts: {e}")
            return []
    
    def get_ltp(self, symbol: str, exchange: str) -> Optional[LTPData]:
        """Get Last Traded Price for a script."""
        if not self.is_connected or not self._smart_api:
            logger.error("Not connected to Angel One")
            return None
        
        try:
            # First search for the token
            search_result = self.search_scripts(symbol, exchange)
            if not search_result:
                logger.error(f"Script {symbol} not found")
                return None
            
            token = search_result[0].token
            
            # Get LTP data using ltpData method
            response = self._smart_api.ltpData(exchange, symbol, token)
            
            if response and response.get('status') and response.get('data'):
                data = response['data']
                
                return LTPData(
                    symbol=symbol,
                    ltp=float(data.get('ltp', 0)),
                    volume=int(data.get('volume', 0)),
                    timestamp=datetime.now().isoformat(),
                    change=float(data.get('netChange', 0)),
                    change_percent=float(data.get('percentChange', 0))
                )
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get LTP for {symbol}: {e}")
            return None
    
    def get_ltp_bulk(self, scripts: List[tuple]) -> Dict[str, LTPData]:
        """Get LTP for multiple scripts."""
        result = {}
        for symbol, exchange in scripts:
            ltp_data = self.get_ltp(symbol, exchange)
            if ltp_data:
                result[symbol] = ltp_data
        return result
    
    def add_active_script(self, symbol: str, exchange: str) -> bool:
        """Add a script to active monitoring list."""
        try:
            # Check if already exists
            for script in self._active_scripts:
                if script.symbol == symbol and script.exchange == exchange:
                    logger.warning(f"Script {symbol} already in active list")
                    return True
            
            # Search for the script
            results = self.search_scripts(symbol, exchange)
            if not results:
                logger.error(f"Script {symbol} not found")
                return False
            
            self._active_scripts.append(results[0])
            logger.info(f"Added {symbol} to active scripts")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add active script: {e}")
            return False
    
    def remove_active_script(self, symbol: str, exchange: str) -> bool:
        """Remove a script from active monitoring list."""
        try:
            initial_count = len(self._active_scripts)
            self._active_scripts = [s for s in self._active_scripts 
                                   if not (s.symbol == symbol and s.exchange == exchange)]
            
            if len(self._active_scripts) < initial_count:
                logger.info(f"Removed {symbol} from active scripts")
                return True
            else:
                logger.warning(f"Script {symbol} not found in active list")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove active script: {e}")
            return False
    
    def subscribe_live_data(self, callback) -> bool:
        """Subscribe to live market data feed."""
        if not self.is_connected or not self._feed_token or not self._client_id:
            logger.error("Not connected to Angel One")
            return False
        
        if not SMARTAPI_AVAILABLE:
            logger.error("SmartApi library not available")
            return False
        
        try:
            # Prepare token list for subscription
            token_list = []
            for script in self._active_scripts:
                token_list.append({
                    "exchangeType": self._get_exchange_type(script.exchange),
                    "tokens": [script.token]
                })
            
            if not token_list:
                logger.warning("No active scripts to subscribe")
                return False
            
            # Initialize WebSocket
            correlation_id = "stream_1"
            action = 1  # Subscribe
            mode = 1  # LTP mode
            
            self._websocket = SmartWebSocketV2(
                auth_token=self._session_token,
                api_key=self._api_key,
                client_code=self._client_id,
                feed_token=self._feed_token
            )
            
            def on_data(ws, message):
                """Callback for market data."""
                try:
                    callback(message)
                except Exception as e:
                    logger.error(f"Error in data callback: {e}")
            
            def on_open(ws):
                """Callback on connection open."""
                logger.info("WebSocket connection opened")
                ws.subscribe(correlation_id, mode, token_list)
            
            def on_error(ws, error):
                """Callback on error."""
                logger.error(f"WebSocket error: {error}")
            
            def on_close(ws):
                """Callback on connection close."""
                logger.info("WebSocket connection closed")
            
            self._websocket.on_open = on_open
            self._websocket.on_data = on_data
            self._websocket.on_error = on_error
            self._websocket.on_close = on_close
            
            self._websocket.connect()
            
            logger.info("Subscribed to live data feed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to subscribe to live data: {e}")
            return False
    
    def _get_exchange_type(self, exchange: str) -> int:
        """Get exchange type code for WebSocket."""
        exchange_map = {
            "NSE": 1,
            "NFO": 2,
            "BSE": 3,
            "BFO": 4,
            "MCX": 5,
            "NCDS": 7,
            "NCDEX": 7
        }
        return exchange_map.get(exchange.upper(), 1)
    
    def unsubscribe_live_data(self) -> bool:
        """Unsubscribe from live market data feed."""
        try:
            if self._websocket:
                self._websocket.close()
                self._websocket = None
            
            logger.info("Unsubscribed from live data feed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to unsubscribe from live data: {e}")
            return False
