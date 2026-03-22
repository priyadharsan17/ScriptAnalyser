import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "."

Item {
    id: root
    
    // Listen to navigation signal from backend
    Connections {
        target: homeBackend
        function onCardNavigate(screenName) {
            screenNavigator.navigateTo(screenName)
        }
    }
    
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
                width: parent.width - Theme.spacingXLarge * 2
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: Theme.spacingXLarge
                spacing: Theme.spacingLarge
                
                // Header section
                Rectangle {
                    Layout.fillWidth: true
                    height: 120
                    color: Theme.surface
                    radius: Theme.radiusLarge
                    border.color: Theme.cardBorder
                    border.width: 1
                    
                    layer.enabled: true
                    layer.effect: DropShadow {
                        transparentBorder: true
                        horizontalOffset: 0
                        verticalOffset: 2
                        radius: 12
                        samples: 25
                        color: "#30000000"
                    }
                    
                    RowLayout {
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.verticalCenter: parent.verticalCenter
                        anchors.leftMargin: Theme.spacingLarge
                        anchors.rightMargin: Theme.spacingLarge
                        spacing: Theme.spacingMedium
                        
                        // User avatar
                        Rectangle {
                            width: 80
                            height: 80
                            radius: 40
                            color: Theme.primary
                            
                            Text {
                                anchors.centerIn: parent
                                text: homeBackend.username.length > 0 ? homeBackend.username.charAt(0).toUpperCase() : "U"
                                font.pixelSize: Theme.fontSizeXXLarge
                                font.bold: true
                                color: "white"
                            }
                        }
                        
                        // User info
                        ColumnLayout {
                            spacing: Theme.spacingSmall
                            
                            Text {
                                text: "Welcome back,"
                                font.pixelSize: Theme.fontSizeNormal
                                color: Theme.textSecondary
                            }
                            
                            Text {
                                text: homeBackend.username
                                font.pixelSize: Theme.fontSizeXLarge
                                font.bold: true
                                color: Theme.textPrimary
                            }
                            
                            Text {
                                text: "Last login: " + homeBackend.loginTime
                                font.pixelSize: Theme.fontSizeSmall
                                color: Theme.textTertiary
                            }
                        }
                        
                        // Spacer to push logout button to right
                        Item {
                            Layout.fillWidth: true
                        }
                        
                        // Logout button
                        CustomButton {
                            width: 120
                            height: 40
                            text: "Logout"
                            buttonColor: Theme.error
                            hoverColor: "#dc2626"
                            pressedColor: "#b91c1c"
                            textColor: "#ffffff"
                            onClicked: screenNavigator.navigateTo("login")
                        }
                    }
                }
                
                // Dashboard title
                Text {
                    text: "Dashboard"
                    font.pixelSize: Theme.fontSizeXLarge
                    font.bold: true
                    color: Theme.textPrimary
                    Layout.topMargin: Theme.spacingNormal
                }
                
                Text {
                    text: "Select a module to get started"
                    font.pixelSize: Theme.fontSizeNormal
                    color: Theme.textSecondary
                }
                
                // Cards grid
                GridLayout {
                    Layout.fillWidth: true
                    columns: 2
                    rowSpacing: Theme.spacingLarge
                    columnSpacing: Theme.spacingLarge
                    
                    // Script Analysis Card
                    DashboardCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 280
                        
                        title: "Script Analysis"
                        description: "Analyze and monitor your trading scripts in real-time"
                        iconText: "📊"
                        accentColor: Theme.primary
                        
                        onCardClicked: homeBackend.cardClicked("Script Analysis")
                    }
                    
                    // Notification Management Card
                    DashboardCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 280
                        
                        title: "Notification Management"
                        description: "Configure and manage stock price alerts and notifications"
                        iconText: "🔔"
                        accentColor: Theme.secondary
                        
                        onCardClicked: homeBackend.cardClicked("Notification Management")
                    }
                    
                    // Settings Card
                    DashboardCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 280
                        
                        title: "Settings"
                        description: "Customize your preferences and application settings"
                        iconText: "⚙️"
                        accentColor: Theme.warning
                        
                        onCardClicked: homeBackend.cardClicked("Settings")
                    }
                    
                    // About Card
                    DashboardCard {
                        Layout.fillWidth: true
                        Layout.preferredHeight: 280
                        
                        title: "About"
                        description: "Learn more about Stock Notification Manager and its features"
                        iconText: "ℹ️"
                        accentColor: Theme.info
                        
                        onCardClicked: homeBackend.cardClicked("About")
                    }
                }
            }
        }
    }
    
    // Reusable Dashboard Card
    component DashboardCard: Rectangle {
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
        opacity: cardArea.containsMouse ? 0.05 : 0
        radius: parent.radius
        
        Behavior on opacity { NumberAnimation { duration: Theme.animationDuration } }
    }
    
    // Left accent bar
    Rectangle {
        width: 4
        height: parent.height - 32
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        color: card.accentColor
        radius: 2
        opacity: cardArea.containsMouse ? 1 : 0.5
        
        Behavior on opacity { NumberAnimation { duration: Theme.animationDuration } }
    }
    
    ColumnLayout {
        anchors.fill: parent
        anchors.margins: Theme.spacingLarge
        anchors.leftMargin: Theme.spacingLarge + 12
        spacing: Theme.spacingNormal
        
        // Icon
        Text {
            text: card.iconText
            font.pixelSize: 48
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
            font.pixelSize: Theme.fontSizeNormal
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