import QtQuick 2.15
import QtQuick.Controls 2.15
import "."

Rectangle {
    id: root
    
    property string text: ""
    property bool enabled: true
    property color buttonColor: Theme.primary
    property color hoverColor: Theme.primaryLight
    property color pressedColor: Theme.primaryDark
    property color textColor: "#ffffff"
    property int fontSize: Theme.fontSizeMedium
    property bool fontBold: true
    
    signal clicked()
    
    implicitWidth: 120
    implicitHeight: 50
    
    color: !enabled ? Theme.surfaceLight :
           mouseArea.pressed ? pressedColor : 
           mouseArea.containsMouse ? hoverColor : buttonColor
    
    radius: Theme.radiusNormal
    opacity: enabled ? 1 : 0.5
    
    Behavior on color { 
        ColorAnimation { duration: Theme.animationDuration } 
    }
    
    Text {
        anchors.centerIn: parent
        text: root.text
        color: root.textColor
        font.pixelSize: root.fontSize
        font.bold: root.fontBold
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        cursorShape: enabled ? Qt.PointingHandCursor : Qt.ArrowCursor
        enabled: root.enabled
        onClicked: root.clicked()
    }
}
