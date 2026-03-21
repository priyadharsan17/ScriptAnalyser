import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15
import "qml"

Window {
    id: mainWindow
    width: 1920
    height: 1080
    visible: true
    title: "Stock Notification Manager"
    color: Theme.background
    
    // Screen container with transitions
    Item {
        id: screenContainer
        anchors.fill: parent
        
        // Login Screen
        Loader {
            id: loginLoader
            anchors.fill: parent
            source: "qml/Login.qml"
            active: screenNavigator.currentScreen === "login"
            visible: active
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.animationDurationSlow }
            }
            
            opacity: active ? 1 : 0
            
            Connections {
                target: loginLoader.item ? loginBackend : null
                function onLoginSuccess(username) {
                    homeBackend.username = username
                    screenNavigator.navigateTo("home")
                }
            }
        }
        
        // Home Screen
        Loader {
            id: homeLoader
            anchors.fill: parent
            source: "qml/HomeScreen.qml"
            active: screenNavigator.currentScreen === "home"
            visible: active
            
            Behavior on opacity {
                NumberAnimation { duration: Theme.animationDurationSlow }
            }
            
            opacity: active ? 1 : 0
        }
    }
}
