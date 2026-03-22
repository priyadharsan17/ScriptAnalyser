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
                            onClicked: screenNavigator.navigateTo("home")
                        }
                        
                        // Title
                        Text {
                            Layout.fillWidth: true
                            text: "Settings"
                            font.pixelSize: Theme.fontSizeXLarge
                            font.bold: true
                            color: Theme.textPrimary
                            verticalAlignment: Text.AlignVCenter
                        }
                    }
                }
                
                // Settings Categories
                Text {
                    text: "Categories"
                    font.pixelSize: Theme.fontSizeLarge
                    font.bold: true
                    color: Theme.textPrimary
                    Layout.topMargin: Theme.spacingNormal
                }
                
                // Settings Cards Grid
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    rowSpacing: Theme.spacingLarge
                    columnSpacing: Theme.spacingLarge
                    
                    // Angel One Settings Card
                    SettingsCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        
                        title: "Angel One Settings"
                        description: "Configure Angel One broker API credentials and connection settings"
                        iconText: "🔑"
                        accentColor: "#FF6B35"
                        
                        onCardClicked: screenNavigator.navigateTo("angelOneSettings")
                    }
                    
                    // WhatsApp Settings Card
                    SettingsCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        
                        title: "WhatsApp Settings"
                        description: "Configure WhatsApp messenger for notifications"
                        iconText: "💬"
                        accentColor: "#25D366"
                        
                        onCardClicked: {
                            // TODO: Navigate to WhatsApp settings
                        }
                    }
                    
                    // Telegram Settings Card
                    SettingsCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        
                        title: "Telegram Settings"
                        description: "Configure Telegram bot for notifications"
                        iconText: "📱"
                        accentColor: "#0088cc"
                        
                        onCardClicked: screenNavigator.navigateTo("telegramSettings")
                    }
                    
                    // Application Settings Card
                    SettingsCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 200
                        
                        title: "Application Settings"
                        description: "General application preferences and configurations"
                        iconText: "🎛️"
                        accentColor: Theme.primary
                        
                        onCardClicked: {
                            // TODO: Navigate to App settings
                        }
                    }
                }
            }
        }
    }
    
    // Reusable Settings Card
    component SettingsCard: Rectangle {
        id: card
        
        property string title: ""
        property string description: ""
        property string iconText: ""
        property color accentColor: Theme.primary
        signal cardClicked()
        
        color: Theme.cardBackground
        radius: Theme.radiusLarge
        border.color: Theme.cardBorder
        border.width: 1
        
        layer.enabled: true
        layer.effect: DropShadow {
            transparentBorder: true
            horizontalOffset: 0
            verticalOffset: 4
            radius: 12
            samples: 25
            color: "#30000000"
        }
        
        // Hover effect
        Rectangle {
            anchors.fill: parent
            color: card.accentColor
            opacity: cardArea.containsMouse ? 0.08 : 0
            radius: parent.radius
            
            Behavior on opacity { NumberAnimation { duration: Theme.animationDuration } }
        }
        
        // Left accent bar
        Rectangle {
            width: 4
            height: parent.height - 24
            anchors.left: parent.left
            anchors.leftMargin: 12
            anchors.verticalCenter: parent.verticalCenter
            color: card.accentColor
            radius: 2
            opacity: cardArea.containsMouse ? 1 : 0.6
            
            Behavior on opacity { NumberAnimation { duration: Theme.animationDuration } }
        }
        
        ColumnLayout {
            anchors.fill: parent
            anchors.margins: Theme.spacingLarge
            anchors.leftMargin: Theme.spacingLarge + 8
            spacing: Theme.spacingNormal
            
            // Icon
            Text {
                text: card.iconText
                font.pixelSize: 40
                Layout.alignment: Qt.AlignLeft
            }
            
            // Title
            Text {
                text: card.title
                font.pixelSize: Theme.fontSizeLarge
                font.bold: true
                color: Theme.textPrimary
            }
            
            // Description
            Text {
                Layout.fillWidth: true
                text: card.description
                font.pixelSize: Theme.fontSizeSmall
                color: Theme.textSecondary
                wrapMode: Text.WordWrap
            }
            
            Item { Layout.fillHeight: true }
        }
        
        MouseArea {
            id: cardArea
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.PointingHandCursor
            onClicked: card.cardClicked()
        }
    }
}
