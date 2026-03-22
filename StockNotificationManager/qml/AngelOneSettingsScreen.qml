import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "."

Item {
    id: root
    
    Rectangle {
        anchors.fill: parent
        color: Theme.background
        
        // Background gradient
        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.gradientTop }
                GradientStop { position: 1.0; color: Theme.gradientBottom }
            }
        }
        
        // Main content with scrolling
        Flickable {
            anchors.fill: parent
            contentHeight: mainLayout.height + Theme.spacingXLarge * 2
            clip: true
            
            ColumnLayout {
                id: mainLayout
                width: parent.width - Theme.spacingLarge * 2
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: Theme.spacingXLarge
                spacing: Theme.spacingLarge
                
                // Header section
                Rectangle {
                    Layout.fillWidth: true
                    height: 80
                    color: Theme.surface
                    radius: Theme.radiusLarge
                    border.color: Theme.cardBorder
                    border.width: 1
                    
                    layer.enabled: true
                    layer.effect: DropShadow {
                        transparentBorder: true
                        horizontalOffset: 0
                        verticalOffset: 2
                        radius: 8
                        samples: 17
                        color: "#20000000"
                    }
                    
                    RowLayout {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: Theme.spacingLarge
                        anchors.rightMargin: Theme.spacingLarge
                        spacing: Theme.spacingLarge
                        
                        // Back button
                        CustomButton {
                            width: 100
                            height: 40
                            text: "← Back"
                            buttonColor: Theme.surfaceLight
                            hoverColor: Theme.surfaceHover
                            pressedColor: "#e0e0e0"
                            textColor: Theme.textPrimary
                            onClicked: screenNavigator.navigateTo("settings")
                        }
                        
                        // Title
                        Text {
                            Layout.fillWidth: true
                            text: "Angel One Settings"
                            font.pixelSize: Theme.fontSizeXLarge
                            font.bold: true
                            color: Theme.textPrimary
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                // Status Message
                Rectangle {
                    id: statusMessage
                    Layout.fillWidth: true
                    height: statusText.visible ? 60 : 0
                    visible: height > 0
                    color: statusText.isError ? "#fee2e2" : "#d1fae5"
                    border.color: statusText.isError ? "#fca5a5" : "#6ee7b7"
                    border.width: 1
                    radius: Theme.radiusNormal
                    
                    Behavior on height { NumberAnimation { duration: 200 } }
                    
                    Text {
                        id: statusText
                        anchors.centerIn: parent
                        text: ""
                        font.pixelSize: Theme.fontSizeNormal
                        color: isError ? "#991b1b" : "#065f46"
                        visible: text !== ""
                        
                        property bool isError: false
                    }
                }
                
                // Settings Form
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: formLayout.height + Theme.spacingXLarge * 2
                    color: Theme.surface
                    radius: Theme.radiusLarge
                    border.color: Theme.cardBorder
                    border.width: 1
                    
                    layer.enabled: true
                    layer.effect: DropShadow {
                        transparentBorder: true
                        horizontalOffset: 0
                        verticalOffset: 2
                        radius: 8
                        samples: 17
                        color: "#20000000"
                    }
                    
                    ColumnLayout {
                        id: formLayout
                        width: parent.width - Theme.spacingXLarge * 2
                        anchors.centerIn: parent
                        spacing: Theme.spacingLarge
                        
                        // API Key Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "API Key *"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: apiKeyField
                                Layout.fillWidth: true
                                placeholder: "Enter your Angel One API Key"
                                
                                Component.onCompleted: {
                                    angelOneSettingsBackend.loadSettings()
                                }
                                
                                Connections {
                                    target: angelOneSettingsBackend
                                    function onSettingsLoaded(settingsJson) {
                                        var settings = JSON.parse(settingsJson)
                                        apiKeyField.text = settings.api_key || ""
                                        clientIdField.text = settings.client_id || ""
                                        passwordField.text = settings.password || ""
                                        totpSecretField.text = settings.totp_secret || ""
                                    }
                                }
                            }
                        }
                        
                        // Client ID Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Client ID *"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: clientIdField
                                Layout.fillWidth: true
                                placeholder: "Enter your Client ID"
                            }
                        }
                        
                        // Password Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Password *"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: passwordField
                                Layout.fillWidth: true
                                placeholder: "Enter your Password"
                                isPassword: true
                            }
                        }
                        
                        // TOTP Secret Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            RowLayout {
                                spacing: Theme.spacingSmall
                                
                                Text {
                                    text: "TOTP Secret"
                                    font.pixelSize: Theme.fontSizeNormal
                                    font.bold: true
                                    color: Theme.textPrimary
                                }
                                
                                Text {
                                    text: "(Optional)"
                                    font.pixelSize: Theme.fontSizeSmall
                                    color: Theme.textTertiary
                                }
                            }
                            
                            CustomTextField {
                                id: totpSecretField
                                Layout.fillWidth: true
                                placeholder: "Enter TOTP Secret if 2FA is enabled"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Leave blank if you don't use 2-Factor Authentication"
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textTertiary
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        // Action Buttons
                        RowLayout {
                            Layout.fillWidth: true
                            Layout.topMargin: Theme.spacingNormal
                            spacing: Theme.spacingNormal
                            
                            CustomButton {
                                Layout.fillWidth: true
                                height: 50
                                text: saveButton.saving ? "Saving..." : "Save Settings"
                                buttonColor: Theme.primary
                                hoverColor: "#2563eb"
                                pressedColor: "#1d4ed8"
                                textColor: "#ffffff"
                                enabled: !saveButton.saving
                                
                                property bool saving: false
                                id: saveButton
                                
                                onClicked: {
                                    var settings = {
                                        "api_key": apiKeyField.text.trim(),
                                        "client_id": clientIdField.text.trim(),
                                        "password": passwordField.text.trim(),
                                        "totp_secret": totpSecretField.text.trim()
                                    }
                                    
                                    saving = true
                                    angelOneSettingsBackend.saveSettings(settings)
                                }
                                
                                Connections {
                                    target: angelOneSettingsBackend
                                    function onSettingsSaved(success, message) {
                                        saveButton.saving = false
                                        statusText.text = message
                                        statusText.isError = !success
                                        
                                        // Hide message after 3 seconds
                                        statusMessageTimer.restart()
                                    }
                                }
                            }
                            
                            CustomButton {
                                Layout.fillWidth: true
                                height: 50
                                text: testButton.testing ? "Testing..." : "Test Connection"
                                buttonColor: Theme.secondary
                                hoverColor: "#7c3aed"
                                pressedColor: "#6d28d9"
                                textColor: "#ffffff"
                                enabled: !testButton.testing
                                
                                property bool testing: false
                                id: testButton
                                
                                onClicked: {
                                    testing = true
                                    angelOneSettingsBackend.testConnection()
                                }
                                
                                Connections {
                                    target: angelOneSettingsBackend
                                    function onConnectionTested(success, message) {
                                        testButton.testing = false
                                        statusText.text = message
                                        statusText.isError = !success
                                        
                                        // Hide message after 5 seconds for test results
                                        statusMessageTimer.interval = 5000
                                        statusMessageTimer.restart()
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Help Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: helpLayout.height + Theme.spacingLarge * 2
                    color: "#eff6ff"
                    radius: Theme.radiusNormal
                    border.color: "#bfdbfe"
                    border.width: 1
                    
                    ColumnLayout {
                        id: helpLayout
                        width: parent.width - Theme.spacingLarge * 2
                        anchors.centerIn: parent
                        spacing: Theme.spacingSmall
                        
                        Text {
                            text: "ℹ️ Help"
                            font.pixelSize: Theme.fontSizeNormal
                            font.bold: true
                            color: "#1e40af"
                        }
                        
                        Text {
                            Layout.fillWidth: true
                            text: "• Get your API credentials from Angel One SmartAPI portal\n• TOTP Secret is only required if you have 2FA enabled\n• Click 'Test Connection' to verify your credentials\n• Your password is stored securely"
                            font.pixelSize: Theme.fontSizeSmall
                            color: "#1e40af"
                            wrapMode: Text.WordWrap
                            lineHeight: 1.4
                        }
                    }
                }
            }
        }
    }
    
    // Timer to hide status message
    Timer {
        id: statusMessageTimer
        interval: 3000
        onTriggered: {
            statusText.text = ""
            interval = 3000 // Reset to default
        }
    }
}
