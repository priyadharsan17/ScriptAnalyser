import QtQuick 2.15
import QtQuick.Controls 2.15
import "."

Item {
    id: root
    
    property string label: ""
    property string placeholder: ""
    property string text: ""
    property bool isPassword: false
    property color labelColor: Theme.textSecondary
    property color backgroundColor: Theme.inputBackground
    property color borderColor: Theme.inputBorder
    property color focusBorderColor: Theme.inputFocus
    property color textColor: Theme.textPrimary
    property color placeholderColor: Theme.textTertiary
    
    signal returnPressed()
    signal textEdited(string text)
    
    implicitWidth: 300
    implicitHeight: label ? 80 : 50
    
    Column {
        anchors.fill: parent
        spacing: Theme.spacingSmall
        
        // Label
        Text {
            text: root.label
            color: root.labelColor
            font.pixelSize: Theme.fontSizeNormal
            visible: root.label !== ""
        }
        
        // Input field
        Rectangle {
            width: parent.width
            height: 50
            color: root.backgroundColor
            border.color: textInput.activeFocus ? root.focusBorderColor : root.borderColor
            border.width: textInput.activeFocus ? 2 : 1
            radius: Theme.radiusNormal
            
            Behavior on border.color {
                ColorAnimation { duration: Theme.animationDuration }
            }
            
            Behavior on border.width {
                NumberAnimation { duration: Theme.animationDuration }
            }
            
            TextInput {
                id: textInput
                anchors.fill: parent
                anchors.margins: Theme.spacingNormal
                color: root.textColor
                font.pixelSize: Theme.fontSizeNormal
                verticalAlignment: Text.AlignVCenter
                echoMode: root.isPassword ? TextInput.Password : TextInput.Normal
                clip: true
                selectByMouse: true
                
                onTextChanged: {
                    root.text = text
                    root.textEdited(text)
                }
                
                Keys.onReturnPressed: root.returnPressed()
                
                Text {
                    anchors.fill: parent
                    text: root.placeholder
                    color: root.placeholderColor
                    font.pixelSize: Theme.fontSizeNormal
                    verticalAlignment: Text.AlignVCenter
                    visible: !textInput.text && !textInput.activeFocus
                }
            }
        }
    }
    
    function forceActiveFocus() {
        textInput.forceActiveFocus()
    }
    
    function clear() {
        textInput.text = ""
    }
}
