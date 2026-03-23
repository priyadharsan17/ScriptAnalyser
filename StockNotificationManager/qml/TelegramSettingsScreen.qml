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
                                        console.log("Settings loaded:", settingsJson)
                                        var settings = JSON.parse(settingsJson)
                                        console.log("Bot token:", settings.bot_token)
                                        console.log("Stock chat ID:", settings.stock_notification_chat_id)
                                        console.log("Threshold chat ID:", settings.threshold_notification_chat_id)
                                        botTokenField.text = settings.bot_token || ""
                                        stockChatIdField.text = settings.stock_notification_chat_id || ""
                                        thresholdChatIdField.text = settings.threshold_notification_chat_id || ""
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
                        
                        // Fetch Chat IDs Button
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            CustomButton {
                                Layout.fillWidth: true
                                height: 50
                                text: fetchChatIdsButton.fetching ? "Fetching... (Send messages to your groups)" : "🔍 Fetch Chat IDs"
                                buttonColor: Theme.info
                                hoverColor: "#2563eb"
                                pressedColor: "#1d4ed8"
                                textColor: "#ffffff"
                                enabled: !fetchChatIdsButton.fetching && botTokenField.text.trim() !== ""
                                
                                property bool fetching: false
                                id: fetchChatIdsButton
                                
                                onClicked: {
                                    fetching = true
                                    telegramSettingsBackend.fetchChatId()
                                }
                                
                                Connections {
                                    target: telegramSettingsBackend
                                    function onChatIdFetched(chatsJson, success, message) {
                                        console.log("Fetch chat IDs - received:", chatsJson, success, message)
                                        fetchChatIdsButton.fetching = false
                                        
                                        if (success) {
                                            var chats = JSON.parse(chatsJson)
                                            console.log("Parsed chats:", JSON.stringify(chats))
                                            if (chats.length > 0) {
                                                chatSelectionPopup.chats = chats
                                                chatSelectionPopup.open()
                                            } else {
                                                statusText.text = "No chats found. Please send messages and try again."
                                                statusText.isError = true
                                                statusMessageTimer.restart()
                                            }
                                        } else {
                                            statusText.text = message
                                            statusText.isError = true
                                            statusMessageTimer.restart()
                                        }
                                    }
                                }
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Click to fetch all chat IDs. After clicking, send messages to your groups within 30 seconds."
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textTertiary
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        // Stock Notification Group Chat ID
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Stock Notification Group Chat ID *"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: stockChatIdField
                                Layout.fillWidth: true
                                placeholder: "Enter manually or fetch above"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Chat ID for stock notifications"
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textTertiary
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        // Threshold Notification Group Chat ID
                        ColumnLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Threshold Notification Group Chat ID"
                                font.pixelSize: Theme.fontSizeNormal
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            CustomTextField {
                                id: thresholdChatIdField
                                Layout.fillWidth: true
                                placeholder: "Enter manually or fetch above (optional)"
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Chat ID for threshold notifications (optional)"
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
                                        "bot_token": botTokenField.text.trim(),
                                        "stock_notification_chat_id": stockChatIdField.text.trim(),
                                        "threshold_notification_chat_id": thresholdChatIdField.text.trim()
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
                        
                        // Section Header
                        Text {
                            text: "🧪 Test Message"
                            font.pixelSize: Theme.fontSizeLarge
                            font.bold: true
                            color: Theme.textPrimary
                        }
                        
                        // Group Selection
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
                                Layout.preferredHeight: 45
                                
                                textRole: "name"
                                valueRole: "chat_id"
                                
                                model: []
                                
                                contentItem: Text {
                                    leftPadding: Theme.spacingNormal
                                    rightPadding: (groupComboBox.indicator ? groupComboBox.indicator.width : 0) + groupComboBox.spacing
                                    
                                    text: groupComboBox.displayText
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    verticalAlignment: Text.AlignVCenter
                                    elide: Text.ElideRight
                                }
                                
                                background: Rectangle {
                                    implicitWidth: 200
                                    implicitHeight: 45
                                    color: groupComboBox.pressed ? Theme.surfaceHover : Theme.surfaceLight
                                    border.color: groupComboBox.activeFocus ? Theme.primary : Theme.cardBorder
                                    border.width: 1
                                    radius: Theme.radiusNormal
                                }
                                
                                popup: Popup {
                                    y: groupComboBox.height - 1
                                    width: groupComboBox.width
                                    implicitHeight: contentItem.implicitHeight
                                    padding: 1
                                    
                                    contentItem: ListView {
                                        clip: true
                                        implicitHeight: contentHeight
                                        model: groupComboBox.popup.visible ? groupComboBox.delegateModel : null
                                        currentIndex: groupComboBox.highlightedIndex
                                        
                                        ScrollIndicator.vertical: ScrollIndicator { }
                                    }
                                    
                                    background: Rectangle {
                                        color: Theme.surface
                                        border.color: Theme.cardBorder
                                        border.width: 1
                                        radius: Theme.radiusNormal
                                    }
                                }
                                
                                delegate: ItemDelegate {
                                    width: groupComboBox.width
                                    contentItem: Text {
                                        text: modelData.name
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: Theme.textPrimary
                                        verticalAlignment: Text.AlignVCenter
                                        elide: Text.ElideRight
                                    }
                                    highlighted: groupComboBox.highlightedIndex === index
                                    background: Rectangle {
                                        color: highlighted ? Theme.primaryLight : "transparent"
                                    }
                                }
                            }
                            
                            Text {
                                Layout.fillWidth: true
                                text: "Click 'Load Groups' to populate this list"
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textTertiary
                                wrapMode: Text.WordWrap
                            }
                        }
                        
                        // Message Input
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
                                Layout.preferredHeight: 120
                                color: Theme.surfaceLight
                                border.color: messageInput.activeFocus ? Theme.primary : Theme.cardBorder
                                border.width: 1
                                radius: Theme.radiusNormal
                                
                                ScrollView {
                                    anchors.fill: parent
                                    anchors.margins: 1
                                    
                                    TextArea {
                                        id: messageInput
                                        placeholderText: "Type your test message here..."
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: Theme.textPrimary
                                        wrapMode: TextArea.Wrap
                                        selectByMouse: true
                                        
                                        background: Rectangle {
                                            color: "transparent"
                                        }
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
                            hoverColor: "#10b981"
                            pressedColor: "#059669"
                            textColor: "#ffffff"
                            enabled: !sendButton.sending && groupComboBox.currentIndex >= 0 && messageInput.text.trim() !== ""
                            
                            property bool sending: false
                            id: sendButton
                            
                            onClicked: {
                                if (groupComboBox.currentIndex >= 0) {
                                    var selectedGroup = groupComboBox.model[groupComboBox.currentIndex]
                                    sending = true
                                    telegramSettingsBackend.sendTestMessage(selectedGroup.chat_id, messageInput.text)
                                }
                            }
                            
                            Connections {
                                target: telegramSettingsBackend
                                function onMessageSent(success, message) {
                                    sendButton.sending = false
                                    statusText.text = message
                                    statusText.isError = !success
                                    statusMessageTimer.restart()
                                    
                                    if (success) {
                                        messageInput.text = ""
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        // Auto-hide status message timer
        Timer {
            id: statusMessageTimer
            interval: 5000
            running: false
            repeat: false
            onTriggered: {
                statusText.text = ""
            }
        }
        
        // Chat Selection Popup
        Rectangle {
            id: chatSelectionPopup
            anchors.centerIn: parent
            width: Math.min(parent.width * 0.8, 600)
            height: Math.min(parent.height * 0.7, 500)
            color: Theme.surface
            radius: Theme.radiusLarge
            border.color: Theme.cardBorder
            border.width: 2
            visible: opacity > 0
            opacity: 0
            z: 1000
            
            property var chats: []
            
            function open() {
                opacity = 1
            }
            
            function close() {
                opacity = 0
            }
            
            Behavior on opacity {
                NumberAnimation { duration: 200 }
            }
            
            // Shadow overlay
            Rectangle {
                anchors.fill: parent
                anchors.margins: -10000
                color: "#80000000"
                visible: chatSelectionPopup.opacity > 0
                z: -1
                
                MouseArea {
                    anchors.fill: parent
                    onClicked: chatSelectionPopup.close()
                }
            }
            
            ColumnLayout {
                anchors.fill: parent
                anchors.margins: Theme.spacingLarge
                spacing: Theme.spacingNormal
                
                // Header
                RowLayout {
                    Layout.fillWidth: true
                    spacing: Theme.spacingNormal
                    
                    Text {
                        Layout.fillWidth: true
                        text: "Select Chat IDs"
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
                        onClicked: chatSelectionPopup.close()
                    }
                }
                
                Text {
                    Layout.fillWidth: true
                    text: "Click on a chat to assign it to Stock or Threshold notifications:"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textSecondary
                    wrapMode: Text.WordWrap
                }
                
                // Chat List
                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: Theme.surfaceLight
                    radius: Theme.radiusNormal
                    border.color: Theme.cardBorder
                    border.width: 1
                    
                    ListView {
                        id: chatListView
                        anchors.fill: parent
                        anchors.margins: Theme.spacingSmall
                        clip: true
                        model: chatSelectionPopup.chats
                        spacing: Theme.spacingSmall
                        
                        delegate: Rectangle {
                            width: chatListView.width - Theme.spacingSmall * 2
                            height: chatItem.height
                            x: Theme.spacingSmall
                            color: "transparent"
                            
                            ColumnLayout {
                                id: chatItem
                                width: parent.width
                                spacing: Theme.spacingSmall
                                
                                Rectangle {
                                    Layout.fillWidth: true
                                    height: chatInfo.height + Theme.spacingNormal * 2
                                    color: Theme.surface
                                    radius: Theme.radiusNormal
                                    border.color: Theme.cardBorder
                                    border.width: 1
                                    
                                    ColumnLayout {
                                        id: chatInfo
                                        anchors.left: parent.left
                                        anchors.right: parent.right
                                        anchors.verticalCenter: parent.verticalCenter
                                        anchors.margins: Theme.spacingNormal
                                        spacing: Theme.spacingSmall
                                        
                                        Text {
                                            text: modelData.title
                                            font.pixelSize: Theme.fontSizeMedium
                                            font.bold: true
                                            color: Theme.textPrimary
                                        }
                                        
                                        Text {
                                            text: "Chat ID: " + modelData.chat_id + " • Type: " + modelData.type
                                            font.pixelSize: Theme.fontSizeSmall
                                            color: Theme.textSecondary
                                        }
                                    }
                                }
                                
                                RowLayout {
                                    Layout.fillWidth: true
                                    spacing: Theme.spacingNormal
                                    
                                    CustomButton {
                                        Layout.fillWidth: true
                                        text: "Stock Notifications"
                                        buttonColor: Theme.primary
                                        hoverColor: "#2563eb"
                                        textColor: "#ffffff"
                                        onClicked: {
                                            stockChatIdField.text = modelData.chat_id
                                            chatSelectionPopup.close()
                                            statusText.text = "Assigned to Stock Notifications: " + modelData.title
                                            statusText.isError = false
                                            statusMessageTimer.restart()
                                        }
                                    }
                                    
                                    CustomButton {
                                        Layout.fillWidth: true
                                        text: "Threshold Notifications"
                                        buttonColor: Theme.secondary
                                        hoverColor: "#059669"
                                        textColor: "#ffffff"
                                        onClicked: {
                                            thresholdChatIdField.text = modelData.chat_id
                                            chatSelectionPopup.close()
                                            statusText.text = "Assigned to Threshold Notifications: " + modelData.title
                                            statusText.isError = false
                                            statusMessageTimer.restart()
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}
