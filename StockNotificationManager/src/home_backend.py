from PySide6.QtCore import QObject, Signal, Slot, Property
from datetime import datetime


class HomeBackend(QObject):
    """Backend logic for the home screen."""
    
    def __init__(self):
        super().__init__()
        self._username = ""
        self._login_time = ""
    
    usernameChanged = Signal(str)
    loginTimeChanged = Signal(str)
    
    @Property(str, notify=usernameChanged)
    def username(self):
        return self._username
    
    @username.setter
    def username(self, value):
        if self._username != value:
            self._username = value
            self._login_time = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            self.usernameChanged.emit(value)
            self.loginTimeChanged.emit(self._login_time)
    
    @Property(str, notify=loginTimeChanged)
    def loginTime(self):
        return self._login_time
    
    @Slot(str)
    def cardClicked(self, cardName):
        """Handle card click events."""
        print(f"Card clicked: {cardName}")
        # Functionality to be implemented later
