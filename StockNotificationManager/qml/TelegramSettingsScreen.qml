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
                            text: "📱 Telegram Settings"
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
                        
                        // Bot Token Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Bot Token *"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: botTokenField
                                Layout.fillWidth: true
                                placeholder: "Enter your Telegram Bot Token"
                                
                                Component.onCompleted: {
                                    telegramSettingsBackend.loadSettings()
                                }
                                
                                Connections {
                                    target: telegramSettingsBackend
                                    function onSettingsLoaded(settingsJson) {
                                        var settings = JSON.parse(settingsJson)
                                        botTokenField.text = settings.bot_token || ""
                                        
                                        // Load chat IDs (handle both array and string)
                                        var chatIds = settings.chat_ids || []
                                        if (typeof chatIds === 'string') {
                                            chatIds = chatIds ? [chatIds] : []
                                        }
                                        chatIdsField.text = chatIds.join(", ")
                                    }
                                }
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Get your bot token from @BotFather on Telegram"
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textTertiary
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        // Chat IDs Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Chat IDs *"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: chatIdsField
                                Layout.fillWidth: true
                                placeholder: "Enter chat IDs separated by commas"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Enter group/channel chat IDs separated by commas (e.g., -1001234567890, -1009876543210)"
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
                                    // Parse chat IDs
                                    var chatIdsText = chatIdsField.text.trim()
                                    var chatIds = chatIdsText ? chatIdsText.split(",").map(function(id) { return id.trim() }).filter(function(id) { return id !== "" }) : []
                                    
                                    var settings = {
                                        "bot_token": botTokenField.text.trim(),
                                        "chat_ids": chatIds
                                    }
                                    
                                    saving = true
                                    telegramSettingsBackend.saveSettings(settings)
                                }
                                
                                Connections {
                                    target: telegramSettingsBackend
                                    function onSettingsSaved(success, message) {
                                        saveButton.saving = false
                                        statusText.text = message
                                        statusText.isError = !success
                                        statusMessageTimer.restart()
                                    }
                                }
                            }
                            
                            CustomButton {
                                Layout.fillWidth: true
                                height: 50
                                text: fetchButton.fetching ? "Loading..." : "Load Groups"
                                buttonColor: Theme.secondary
                                hoverColor: "#7c3aed"
                                pressedColor: "#6d28d9"
                                textColor: "#ffffff"
                                enabled: !fetchButton.fetching
                                
                                property bool fetching: false
                                id: fetchButton
                                
                                onClicked: {
                                    fetching = true
                                    telegramSettingsBackend.fetchGroups()
                                }
                                
                                Connections {
                                    target: telegramSettingsBackend
                                    function onGroupsFetched(groupsJson, success, message) {
                                        fetchButton.fetching = false
                                        
                                        if (success) {
                                            var groups = JSON.parse(groupsJson)
                                            groupComboBox.model = groups
                                            groupComboBox.currentIndex = groups.length > 0 ? 0 : -1
                                            statusText.text = message
                                            statusText.isError = false
                                        } else {
                                            statusText.text = message
                                            statusText.isError = true
                                        }
                                        statusMessageTimer.restart()
                                    }
                                }
                            }
                        }
                    }
                }
                
                // Test Message Section
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: testLayout.height + Theme.spacingXLarge * 2
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
                        id: testLayout
                        width: parent.width - Theme.spacingXLarge * 2
                        anchors.centerIn: parent
                        spacing: Theme.spacingLarge
                        
                        Text {
                            text: "Test Message"
                            font.pixelSize: Theme.fontSizeLarge
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        // Group Selector
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Select Group"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            ComboBox {
                                id: groupComboBox
                                Layout.fillWidth: true
                                height: 50
                                
                                textRole: "name"
                                valueRole: "chat_id"
                                
                                displayText: currentIndex >= 0 ? model[currentIndex].name : "No groups loaded"
                                
                                background: Rectangle {
                                    color: Theme.inputBackground
                                    border.color: Theme.inputBorder
                                    border.width: 1
                                    radius: Theme.radiusNormal
                                }
                                
                                contentItem: Text {
                                    leftPadding: Theme.spacingNormal
                                    text: groupComboBox.displayText
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    verticalAlignment: Text.AlignVCenter
                                }
                            }
                        }
                        
                        // Message Field
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Test Message"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            Rectangle {
                                Layout.fillWidth: true
                                height: 100
                                color: Theme.inputBackground
                                border.color: messageArea.activeFocus ? Theme.inputFocus : Theme.inputBorder
                                border.width: messageArea.activeFocus ? 2 : 1
                                radius: Theme.radiusNormal
                                
                                Behavior on border.color {
                                    ColorAnimation { duration: Theme.animationDuration }
                                }
                                
                                ScrollView {
                                    anchors.fill: parent
                                    anchors.margins: Theme.spacingSmall
                                    
                                    TextArea {
                                        id: messageArea
                                        placeholderText: "Type your test message here..."
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: Theme.textPrimary
                                        wrapMode: TextArea.Wrap
                                        selectByMouse: true
                                        
                                        background: Item {}
                                    }
                                }
                            }
                        }
                        
                        // Send Button
                        CustomButton {
                            Layout.fillWidth: true
                            height: 50
                            text: sendButton.sending ? "Sending..." : "Send Test Message"
                            buttonColor: Theme.success
                            hoverColor: "#059669"
                            pressedColor: "#047857"
                            textColor: "#ffffff"
                            enabled: !sendButton.sending && groupComboBox.currentIndex >= 0
                            
                            property bool sending: false
                            id: sendButton
                            
                            onClicked: {
                                var chatId = groupComboBox.model[groupComboBox.currentIndex].chat_id
                                var message = messageArea.text.trim()
                                
                                if (!message) {
                                    statusText.text = "Please enter a message"
                                    statusText.isError = true
                                    statusMessageTimer.restart()
                                    return
                                }
                                
                                sending = true
                                telegramSettingsBackend.sendTestMessage(chatId, message)
                            }
                            
                            Connections {
                                target: telegramSettingsBackend
                                function onMessageSent(success, message) {
                                    sendButton.sending = false
                                    statusText.text = message
                                    statusText.isError = !success
                                    statusMessageTimer.interval = 5000
                                    statusMessageTimer.restart()
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
                            text: "• Create a bot using @BotFather and get your bot token\n• Add the bot to your group/channel\n• Get chat ID by forwarding a message to @userinfobot\n• Click 'Load Groups' to verify your settings\n• Send a test message to confirm everything works"
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
