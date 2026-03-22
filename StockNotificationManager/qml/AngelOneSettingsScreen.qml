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
                                    connectionStatusPopup.open()
                                    angelOneSettingsBackend.testConnection()
                                }
                                
                                Connections {
                                    target: angelOneSettingsBackend
                                    function onConnectionTested(success, message) {
                                        testButton.testing = false
                                        connectionStatusPopup.setResult(success, message)
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
    
    // Connection Status Popup
    Rectangle {
        id: connectionStatusPopup
        anchors.centerIn: parent
        width: Math.min(parent.width * 0.8, 500)
        height: Math.min(parent.height * 0.6, 450)
        color: Theme.surface
        radius: Theme.radiusLarge
        border.color: Theme.cardBorder
        border.width: 2
        visible: opacity > 0
        opacity: 0
        z: 1000
        
        property bool isLoading: false
        property bool testSuccess: false
        property string testMessage: ""
        
        function open() {
            isLoading = true
            testSuccess = false
            testMessage = ""
            opacity = 1
        }
        
        function close() {
            opacity = 0
            isLoading = false
        }
        
        function setResult(success, message) {
            isLoading = false
            testSuccess = success
            testMessage = message
        }
        
        Behavior on opacity {
            NumberAnimation { duration: 200 }
        }
        
        // Shadow overlay
        Rectangle {
            anchors.fill: parent
            anchors.margins: -10000
            color: "#80000000"
            visible: connectionStatusPopup.opacity > 0
            z: -1
            
            MouseArea {
                anchors.fill: parent
                onClicked: {
                    if (!connectionStatusPopup.isLoading) {
                        connectionStatusPopup.close()
                    }
                }
            }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacingLarge
            spacing: Theme.spacingNormal
            
            // Header
            RowLayout {
                Layout.fillWidth: true
                Layout.preferredHeight: 40
                spacing: Theme.spacingNormal
                
                Text {
                    Layout.fillWidth: true
                    text: "🔗 Connection Test"
                    font.pixelSize: Theme.fontSizeLarge
                    font.bold: true
                    color: Theme.textPrimary
                }
                
                CustomButton {
                    text: "✕"
                    width: 40
                    height: 40
                    buttonColor: Theme.surfaceLight
                    hoverColor: Theme.surfaceHover
                    textColor: Theme.textPrimary
                    enabled: !connectionStatusPopup.isLoading
                    onClicked: connectionStatusPopup.close()
                }
            }
            
            // Content Area
            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: Theme.surfaceLight
                radius: Theme.radiusNormal
                border.color: Theme.cardBorder
                border.width: 1
                clip: true
                
                // Loading State
                ColumnLayout {
                    anchors.centerIn: parent
                    width: parent.width * 0.8
                    spacing: Theme.spacingLarge
                    visible: connectionStatusPopup.isLoading
                    
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter
                        width: 60
                        height: 60
                        color: "transparent"
                        
                        Rectangle {
                            id: connectionSpinner
                            anchors.centerIn: parent
                            width: 50
                            height: 50
                            radius: 25
                            color: "transparent"
                            border.color: Theme.secondary
                            border.width: 4
                            
                            Rectangle {
                                width: 10
                                height: 10
                                radius: 5
                                color: Theme.secondary
                                anchors.horizontalCenter: parent.horizontalCenter
                                anchors.top: parent.top
                            }
                            
                            RotationAnimation {
                                target: connectionSpinner
                                from: 0
                                to: 360
                                duration: 1200
                                loops: Animation.Infinite
                                running: connectionStatusPopup.isLoading
                            }
                        }
                    }
                    
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.fillWidth: true
                        text: "Testing Connection..."
                        font.pixelSize: Theme.fontSizeMedium
                        font.bold: true
                        color: Theme.textPrimary
                        horizontalAlignment: Text.AlignHCenter
                    }
                    
                    Text {
                        Layout.alignment: Qt.AlignHCenter
                        Layout.fillWidth: true
                        text: "Verifying your Angel One credentials"
                        font.pixelSize: Theme.fontSizeNormal
                        color: Theme.textSecondary
                        wrapMode: Text.WordWrap
                        horizontalAlignment: Text.AlignHCenter
                    }
                }
                
                // Result State
                ColumnLayout {
                    anchors.fill: parent
                    anchors.margins: Theme.spacingLarge
                    spacing: Theme.spacingNormal
                    visible: !connectionStatusPopup.isLoading
                    
                    Rectangle {
                        Layout.alignment: Qt.AlignHCenter
                        width: 60
                        height: 60
                        radius: 30
                        color: connectionStatusPopup.testSuccess ? "#d1fae5" : "#fee2e2"
                        border.color: connectionStatusPopup.testSuccess ? "#6ee7b7" : "#fca5a5"
                        border.width: 2
                        
                        Text {
                            anchors.centerIn: parent
                            text: connectionStatusPopup.testSuccess ? "✓" : "✗"
                            font.pixelSize: 36
                            font.bold: true
                            color: connectionStatusPopup.testSuccess ? "#065f46" : "#991b1b"
                        }
                    }
                    
                    Text {
                        Layout.fillWidth: true
                        Layout.alignment: Qt.AlignHCenter
                        text: connectionStatusPopup.testSuccess ? "Connection Successful!" : "Connection Failed"
                        font.pixelSize: Theme.fontSizeMedium
                        font.bold: true
                        color: connectionStatusPopup.testSuccess ? "#065f46" : "#991b1b"
                        horizontalAlignment: Text.AlignHCenter
                        wrapMode: Text.WordWrap
                    }
                    
                    ScrollView {
                        Layout.fillWidth: true
                        Layout.fillHeight: true
                        clip: true
                        
                        Rectangle {
                            width: parent.width
                            implicitHeight: messageText.height + Theme.spacingLarge * 2
                            color: Theme.surface
                            radius: Theme.radiusNormal
                            border.color: Theme.cardBorder
                            border.width: 1
                            
                            Text {
                                id: messageText
                                anchors.fill: parent
                                anchors.margins: Theme.spacingLarge
                                text: connectionStatusPopup.testMessage
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textPrimary
                                wrapMode: Text.WordWrap
                            }
                        }
                    }
                    
                    CustomButton {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 45
                        text: "Close"
                        buttonColor: connectionStatusPopup.testSuccess ? Theme.success : Theme.error
                        hoverColor: connectionStatusPopup.testSuccess ? "#10b981" : "#dc2626"
                        pressedColor: connectionStatusPopup.testSuccess ? "#059669" : "#b91c1c"
                        textColor: "#ffffff"
                        onClicked: connectionStatusPopup.close()
                    }
                }
            }
        }
    }
}
