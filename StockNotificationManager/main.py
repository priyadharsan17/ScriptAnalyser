import sys
import os
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl

# Import backend classes
from src.screen_navigator import ScreenNavigator
from src.login_backend import LoginBackend
from src.home_backend import HomeBackend


def main():
    """Main entry point for the Stock Notification Manager application."""
    
    # Create the application
    app = QGuiApplication(sys.argv)
    app.setApplicationName("Stock Notification Manager")
    app.setOrganizationName("ScriptAnalyser")
    
    # Create QML engine
    engine = QQmlApplicationEngine()
    
    # Get the current directory
    current_dir = Path(__file__).parent
    
    # Create backend instances
    screen_navigator = ScreenNavigator()
    login_backend = LoginBackend()
    home_backend = HomeBackend()
    
    # Register context properties
    root_context = engine.rootContext()
    root_context.setContextProperty("screenNavigator", screen_navigator)
    root_context.setContextProperty("loginBackend", login_backend)
    root_context.setContextProperty("homeBackend", home_backend)
    
    # Add import path for QML modules
    engine.addImportPath(str(current_dir / "qml"))
    
    # Load the main QML file
    qml_file = current_dir / "main.qml"
    engine.load(QUrl.fromLocalFile(str(qml_file)))
    
    # Check if the QML file loaded successfully
    if not engine.rootObjects():
        print("Error: Failed to load QML file")
        return -1
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
