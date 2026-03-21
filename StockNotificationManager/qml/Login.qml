import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Item {
    id: root
    
    function handleLogin() {
        loginBackend.login(usernameField.text, passwordField.text)
    }
    
    Rectangle {
        anchors.fill: parent
        color: Theme.background
        
        // Background gradient overlay
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: "#1e293b" }
                GradientStop { position: 1.0; color: "#0f172a" }
            }
        }
        
        // Decorative circles
        Rectangle {
            width: 600
            height: 600
            radius: 300
            color: Theme.primary
            opacity: 0.05
            anchors.left: parent.left
            anchors.top: parent.top
            anchors.leftMargin: -200
            anchors.topMargin: -200
        }
        
        Rectangle {
            width: 400
            height: 400
            radius: 200
            color: Theme.secondary
            opacity: 0.05
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.rightMargin: -100
            anchors.bottomMargin: -100
        }
        
        // Main content
        ColumnLayout {
            anchors.centerIn: parent
            width: 480
            spacing: Theme.spacingLarge
            
            // Logo and title section
            ColumnLayout {
                Layout.alignment: Qt.AlignHCenter
                spacing: Theme.spacingNormal
                
                Rectangle {
                    Layout.alignment: Qt.AlignHCenter
                    width: 80
                    height: 80
                    radius: Theme.radiusMedium
                    color: Theme.primary
                    
                    Text {
                        anchors.centerIn: parent
                        text: "SN"
                        font.pixelSize: Theme.fontSizeXXLarge
                        font.bold: true
                        color: "white"
                    }
                }
                
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Stock Notification Manager"
                    font.pixelSize: Theme.fontSizeXLarge
                    font.bold: true
                    color: Theme.textPrimary
                }
                
                Text {
                    Layout.alignment: Qt.AlignHCenter
                    text: "Sign in to your account"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textSecondary
                }
            }
            
            // Login card
            Rectangle {
                Layout.fillWidth: true
                height: 400
                color: Theme.surface
                radius: Theme.radiusLarge
                border.color: Theme.cardBorder
                border.width: 1
                
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLarge
                    spacing: Theme.spacingMedium
                    
                    // Error message
                    Rectangle {
                        Layout.fillWidth: true
                        height: 50
                        color: Theme.error
                        opacity: 0.1
                        radius: Theme.radiusNormal
                        visible: loginBackend.errorMessage !== ""
                        
                        Text {
                            anchors.fill: parent
                            anchors.margins: Theme.spacingNormal
                            text: loginBackend.errorMessage
                            color: Theme.error
                            font.pixelSize: Theme.fontSizeNormal
                            verticalAlignment: Text.AlignVCenter
                            wrapMode: Text.WordWrap
                        }
                    }
                    
                    // Username field
                    CustomTextField {
                        id: usernameField
                        Layout.fillWidth: true
                        label: "Username"
                        placeholder: "Enter your username"
                        onReturnPressed: passwordField.forceActiveFocus()
                    }
                    
                    // Password field
                    CustomTextField {
                        id: passwordField
                        Layout.fillWidth: true
                        label: "Password"
                        placeholder: "Enter your password"
                        isPassword: true
                        onReturnPressed: handleLogin()
                    }
                    
                    Item { Layout.fillHeight: true }
                    
                    // Login button
                    CustomButton {
                        id: loginButton
                        Layout.fillWidth: true
                        text: loginBackend.isLoading ? "Signing in..." : "Sign In"
                        enabled: !loginBackend.isLoading
                        onClicked: handleLogin()
                    }
                }
            }
            
            // Footer
            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "© 2026 Stock Notification Manager. All rights reserved."
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textTertiary
            }
        }
    }
}
