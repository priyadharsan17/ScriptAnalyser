from PySide6.QtCore import QObject, Signal, Slot, Property


class LoginBackend(QObject):
    """Backend logic for the login screen."""
    
    loginSuccess = Signal(str)  # Emits username on successful login
    loginFailed = Signal(str)   # Emits error message on failed login
    
    def __init__(self):
        super().__init__()
        self._is_loading = False
        self._error_message = ""
    
    loadingChanged = Signal(bool)
    errorMessageChanged = Signal(str)
    
    @Property(bool, notify=loadingChanged)
    def isLoading(self):
        return self._is_loading
    
    @isLoading.setter
    def isLoading(self, value):
        if self._is_loading != value:
            self._is_loading = value
            self.loadingChanged.emit(value)
    
    @Property(str, notify=errorMessageChanged)
    def errorMessage(self):
        return self._error_message
    
    @errorMessage.setter
    def errorMessage(self, value):
        if self._error_message != value:
            self._error_message = value
            self.errorMessageChanged.emit(value)
    
    @Slot(str, str)
    def login(self, username, password):
        """Attempt to login with the provided credentials."""
        self.isLoading = True
        self.errorMessage = ""
        
        # Simple validation for demo purposes
        if not username or not password:
            self.errorMessage = "Please enter both username and password"
            self.isLoading = False
            self.loginFailed.emit(self.errorMessage)
            return
        
        # For demo: accept any non-empty credentials
        # In production, this would validate against a real authentication system
        if len(username) >= 3 and len(password) >= 6:
            self.isLoading = False
            self.loginSuccess.emit(username)
        else:
            self.errorMessage = "Invalid username or password"
            self.isLoading = False
            self.loginFailed.emit(self.errorMessage)
