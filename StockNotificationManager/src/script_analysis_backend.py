from PySide6.QtCore import QObject, Signal, Slot, Property, QRunnable, QThreadPool
import time


class _FetchPricesTask(QRunnable):
    """Worker runnable to fetch prices without blocking the UI."""

    def __init__(self, broker, symbols, backend):
        super().__init__()
        self.broker = broker
        self.symbols = symbols
        self.backend = backend

    def run(self):
        broker = self.broker

        # Resolve to EQ scripts when possible (use broker.search_scripts)
        resolved = []
        if broker:
            for sym, exch in self.symbols:
                try:
                    results = broker.search_scripts(sym, exch)
                    time.sleep(1)  # Small delay to avoid rapid-fire API calls during search
                except Exception:
                    results = []

                if results:
                    # Prefer symbols ending with -EQ
                    eq = next((s for s in results if s.symbol.endswith('-EQ')), results[0])
                    resolved.append((eq.symbol, exch))
                else:
                    resolved.append((sym, exch))
        else:
            resolved = list(self.symbols)

        print(f"Resolved symbols for sector: {resolved}")  # Debug log to verify symbol resolution

        # Fetch sequentially (no bulk) with a delay between requests
        prices_list = []
        for sym, exch in resolved:
            data = None
            if broker:
                try:
                    data = broker.get_ltp(sym, exch)
                except Exception:
                    data = None

            if data:
                prices_list.append({
                    "symbol": data.symbol,
                    "ltp": data.ltp,
                    "change_percent": data.change_percent,
                    "volume": data.volume,
                    "timestamp": data.timestamp
                })
            else:
                prices_list.append({
                    "symbol": sym,
                    "ltp": None,
                    "change_percent": None,
                    "volume": None,
                    "timestamp": None
                })

            # Delay to avoid rapid-fire API calls (mirror main.py test delay)
            try:
                time.sleep(1)
            except Exception:
                pass
        # Update backend state and emit signal (safe to emit from worker thread)
        try:
            self.backend._prices = prices_list
            self.backend.pricesChanged.emit()
        except Exception:
            pass


class ScriptAnalysisBackend(QObject):
    """Provides sector lists and live price fetching for the Script Analysis screen.

    Use `setBroker()` to provide an authenticated broker instance. Fetching
    runs on the global `QThreadPool` to avoid blocking the UI.
    """

    pricesChanged = Signal()
    sectorsChanged = Signal()

    def __init__(self, broker=None):
        super().__init__()
        self._sectors = ["IT", "BANK", "BEES"]
        self._prices = []
        self._broker = broker
        self._thread_pool = QThreadPool.globalInstance()

    @Property('QVariantList', notify=sectorsChanged)
    def sectors(self):
        return self._sectors

    @Property('QVariantList', notify=pricesChanged)
    def prices(self):
        return self._prices

    @Slot(QObject)
    def setBroker(self, broker):
        """Set the broker instance (e.g., AngelOneBroker) used for live prices."""
        self._broker = broker

    @Slot(str)
    def fetchPrices(self, sector):
        """Schedule a background task to fetch prices for the given sector."""
        sector_map = {
            "IT": [("TCS", "NSE"), ("INFY", "NSE"), ("WIPRO", "NSE")],
            "BANK": [("HDFCBANK", "NSE"), ("ICICIBANK", "NSE"), ("SBIN", "NSE")],
            "BEES": [("NIFTYBEES", "NSE"), ("GOLDBEES", "NSE")]
        }

        symbols = sector_map.get(sector, [])
        if not symbols:
            self._prices = []
            self.pricesChanged.emit()
            return

        task = _FetchPricesTask(self._broker, symbols, self)
        self._thread_pool.start(task)

