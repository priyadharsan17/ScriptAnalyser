from PySide6.QtCore import QObject, Signal, Slot, Property
from datetime import datetime


class HomeBackend(QObject):
    """Backend logic for the home screen."""
    
    cardNavigate = Signal(str)
    
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
        # Navigate to settings screen if Settings card is clicked
        if cardName == "Settings":
            self.cardNavigate.emit("settings")
        elif cardName == "Script Analysis":
            # Navigate to the Script Analysis screen
            self.cardNavigate.emit("scriptAnalysis")
