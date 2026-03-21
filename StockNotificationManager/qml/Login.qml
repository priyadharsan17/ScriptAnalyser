import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import "."

Item {
    id: root
    
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
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSmall
                        
                        Text {
                            text: "Username"
                            color: Theme.textSecondary
                            font.pixelSize: Theme.fontSizeNormal
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            height: 50
                            color: Theme.inputBackground
                            border.color: usernameField.activeFocus ? Theme.inputFocus : Theme.inputBorder
                            border.width: usernameField.activeFocus ? 2 : 1
                            radius: Theme.radiusNormal
                            
                            TextInput {
                                id: usernameField
                                anchors.fill: parent
                                anchors.margins: Theme.spacingNormal
                                color: Theme.textPrimary
                                font.pixelSize: Theme.fontSizeNormal
                                verticalAlignment: Text.AlignVCenter
                                clip: true
                                selectByMouse: true
                                
                                Text {
                                    anchors.fill: parent
                                    text: "Enter your username"
                                    color: Theme.textTertiary
                                    font.pixelSize: Theme.fontSizeNormal
                                    verticalAlignment: Text.AlignVCenter
                                    visible: !usernameField.text && !usernameField.activeFocus
                                }
                                
                                Keys.onReturnPressed: passwordField.forceActiveFocus()
                            }
                        }
                    }
                    
                    // Password field
                    ColumnLayout {
                        Layout.fillWidth: true
                        spacing: Theme.spacingSmall
                        
                        Text {
                            text: "Password"
                            color: Theme.textSecondary
                            font.pixelSize: Theme.fontSizeNormal
                        }
                        
                        Rectangle {
                            Layout.fillWidth: true
                            height: 50
                            color: Theme.inputBackground
                            border.color: passwordField.activeFocus ? Theme.inputFocus : Theme.inputBorder
                            border.width: passwordField.activeFocus ? 2 : 1
                            radius: Theme.radiusNormal
                            
                            TextInput {
                                id: passwordField
                                anchors.fill: parent
                                anchors.margins: Theme.spacingNormal
                                color: Theme.textPrimary
                                font.pixelSize: Theme.fontSizeNormal
                                verticalAlignment: Text.AlignVCenter
                                echoMode: TextInput.Password
                                clip: true
                                selectByMouse: true
                                
                                Text {
                                    anchors.fill: parent
                                    text: "Enter your password"
                                    color: Theme.textTertiary
                                    font.pixelSize: Theme.fontSizeNormal
                                    verticalAlignment: Text.AlignVCenter
                                    visible: !passwordField.text && !passwordField.activeFocus
                                }
                                
                                Keys.onReturnPressed: loginButton.clicked()
                            }
                        }
                    }
                    
                    Item { Layout.fillHeight: true }
                    
                    // Login button
                    Rectangle {
                        id: loginButton
                        Layout.fillWidth: true
                        height: 50
                        color: loginButtonArea.pressed ? Theme.primaryDark : 
                               loginButtonArea.containsMouse ? Theme.primaryLight : Theme.primary
                        radius: Theme.radiusNormal
                        enabled: !loginBackend.isLoading
                        
                        Behavior on color { ColorAnimation { duration: Theme.animationDuration } }
                        
                        Text {
                            anchors.centerIn: parent
                            text: loginBackend.isLoading ? "Signing in..." : "Sign In"
                            color: "white"
                            font.pixelSize: Theme.fontSizeMedium
                            font.bold: true
                        }
                        
                        MouseArea {
                            id: loginButtonArea
                            anchors.fill: parent
                            hoverEnabled: true
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                loginBackend.login(usernameField.text, passwordField.text)
                            }
                        }
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
