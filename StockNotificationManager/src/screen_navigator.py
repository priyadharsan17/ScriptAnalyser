from PySide6.QtCore import QObject, Signal, Slot, Property


class ScreenNavigator(QObject):
    """Manages navigation between screens in the application."""
    
    screenChanged = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._current_screen = "login"
        self._previous_screen = ""
    
    @Property(str, notify=screenChanged)
    def currentScreen(self):
        return self._current_screen
    
    @currentScreen.setter
    def currentScreen(self, screen):
        if self._current_screen != screen:
            self._previous_screen = self._current_screen
            self._current_screen = screen
            self.screenChanged.emit(screen)
    
    @Slot(str)
    def navigateTo(self, screen):
        """Navigate to a specific screen."""
        self.currentScreen = screen
    
    @Slot()
    def goBack(self):
        """Navigate to the previous screen."""
        if self._previous_screen:
            self.navigateTo(self._previous_screen)
