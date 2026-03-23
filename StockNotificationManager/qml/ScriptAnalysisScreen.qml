import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import Qt5Compat.GraphicalEffects
import "."

Item {
    anchors.fill: parent                        // FIX: Item must fill its parent

    Rectangle {
        anchors.fill: parent
        color: Theme.background

        Rectangle {
            anchors.fill: parent
            gradient: Gradient {
                GradientStop { position: 0.0; color: Theme.gradientTop }
                GradientStop { position: 1.0; color: Theme.gradientBottom }
            }
        }

        Flickable {
            anchors.fill: parent
            contentHeight: mainLayout.implicitHeight + Theme.spacingXLarge * 2  // FIX: use implicitHeight
            clip: true

            ColumnLayout {
                id: mainLayout
                width: parent.width - Theme.spacingXLarge * 2
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.top: parent.top
                anchors.topMargin: Theme.spacingXLarge
                spacing: Theme.spacingLarge

                // ── Header bar ──────────────────────────────────────────────
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: 70               // FIX: use implicitHeight so layout respects it
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

                        CustomButton {
                            text: "Back"
                            width: 100
                            height: 40
                            buttonColor: Theme.surfaceLight
                            hoverColor: Theme.surfaceHover
                            textColor: Theme.textPrimary
                            Layout.alignment: Qt.AlignVCenter  // FIX: align button vertically
                            onClicked: screenNavigator.goBack()
                        }

                        Text {
                            text: "Script Analysis"
                            font.pixelSize: Theme.fontSizeLarge
                            font.bold: true
                            color: Theme.textPrimary
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Item { Layout.fillWidth: true }
                    }
                }

                // ── Sector selector ─────────────────────────────────────────
                Rectangle {
                    Layout.fillWidth: true
                    implicitHeight: controlsColumn.implicitHeight + Theme.spacingLarge * 2  // FIX: dynamic height
                    color: Theme.surface
                    radius: Theme.radiusNormal
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
                        id: controlsColumn
                        anchors {
                            left: parent.left
                            right: parent.right
                            top: parent.top
                            margins: Theme.spacingLarge
                        }
                        spacing: Theme.spacingNormal

                        Text {
                            text: "Select Sector"
                            font.pixelSize: Theme.fontSizeNormal
                            font.bold: true
                            color: Theme.textPrimary
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: Theme.spacingNormal

                            ComboBox {
                                id: sectorComboBox
                                Layout.preferredWidth: 300
                                Layout.preferredHeight: 40          // FIX: explicit height prevents collapse
                                model: scriptAnalysisBackend.sectors
                                // FIX: removed invalid textRole: "" — model is a string list,
                                //      ComboBox uses the string directly by default
                                contentItem: Text {
                                    text: sectorComboBox.displayText
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    leftPadding: Theme.spacingNormal
                                    verticalAlignment: Text.AlignVCenter  // FIX: vertical centering
                                }
                            }

                            CustomButton {
                                text: "Load Prices"
                                height: 40                          // FIX: match ComboBox height
                                buttonColor: Theme.primary
                                hoverColor: "#2563eb"
                                textColor: "#ffffff"
                                Layout.alignment: Qt.AlignVCenter
                                onClicked: {
                                    var idx = sectorComboBox.currentIndex
                                    if (idx >= 0) {
                                        scriptAnalysisBackend.fetchPrices(
                                            scriptAnalysisBackend.sectors[idx]
                                        )
                                    }
                                }
                            }

                            Item { Layout.fillWidth: true }      // FIX: push controls left, not stretched
                        }
                    }
                }

                // ── Prices table ─────────────────────────────────────────────
                Rectangle {
                    Layout.fillWidth: true
                    Layout.preferredHeight: 300
                    color: Theme.surface
                    radius: Theme.radiusNormal
                    border.color: Theme.cardBorder
                    border.width: 1

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: Theme.spacingSmall
                        spacing: 0                                  // FIX: no gap between header and rows

                        // ── Table header ──────────────────────────────────
                        Rectangle {
                            Layout.fillWidth: true
                            height: 36
                            color: Theme.surfaceLight               // FIX: distinct header background
                            radius: Theme.radiusSmall

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
                                anchors.fill: parent
                                anchors.leftMargin: Theme.spacingSmall
                                anchors.rightMargin: Theme.spacingSmall
                                spacing: 0

                                Text {
                                    text: "Symbol"
                                    font.bold: true
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    Layout.preferredWidth: 200
                                    Layout.alignment: Qt.AlignVCenter
                                }
                                Text {
                                    text: "LTP (₹)"
                                    font.bold: true
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    Layout.preferredWidth: 120
                                    Layout.alignment: Qt.AlignVCenter
                                    horizontalAlignment: Text.AlignRight  // FIX: numeric column right-aligned
                                }
                                Text {
                                    text: "Change %"
                                    font.bold: true
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    Layout.preferredWidth: 120
                                    Layout.alignment: Qt.AlignVCenter
                                    horizontalAlignment: Text.AlignRight
                                }
                                Text {
                                    text: "Volume"
                                    font.bold: true
                                    font.pixelSize: Theme.fontSizeNormal
                                    color: Theme.textPrimary
                                    Layout.preferredWidth: 160
                                    Layout.alignment: Qt.AlignVCenter
                                    horizontalAlignment: Text.AlignRight
                                }
                            }
                        }

                        // ── Data rows ─────────────────────────────────────
                        ListView {
                            id: pricesList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true                              // FIX: clip rows to the list bounds
                            model: scriptAnalysisBackend.prices

                            delegate: Rectangle {
                                width: pricesList.width
                                height: 42
                                color: index % 2 === 0 ? Theme.surfaceLight : "transparent"

                                RowLayout {
                                    anchors.fill: parent
                                    anchors.leftMargin: Theme.spacingSmall
                                    anchors.rightMargin: Theme.spacingSmall
                                    spacing: 0

                                    Text {
                                        text: modelData.symbol ?? "-"
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: Theme.textPrimary
                                        Layout.preferredWidth: 200
                                        Layout.alignment: Qt.AlignVCenter
                                        elide: Text.ElideRight       // FIX: long names don't overflow
                                    }
                                    Text {
                                        text: modelData.ltp !== null
                                              ? modelData.ltp.toFixed(2)
                                              : "-"
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: Theme.textPrimary
                                        Layout.preferredWidth: 120
                                        Layout.alignment: Qt.AlignVCenter
                                        horizontalAlignment: Text.AlignRight
                                    }
                                    Text {
                                        // FIX: green for gain, red for loss, neutral for zero/null
                                        property real pct: modelData.change_percent ?? 0
                                        text: modelData.change_percent !== null
                                              ? pct.toFixed(2) + "%"
                                              : "-"
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: modelData.change_percent === null
                                               ? Theme.textPrimary
                                               : (pct > 0 ? Theme.positive : (pct < 0 ? Theme.negative : Theme.textPrimary))
                                        Layout.preferredWidth: 120
                                        Layout.alignment: Qt.AlignVCenter
                                        horizontalAlignment: Text.AlignRight
                                    }
                                    Text {
                                        text: modelData.volume !== null
                                              ? modelData.volume.toLocaleString()  // FIX: formatted with commas
                                              : "-"
                                        font.pixelSize: Theme.fontSizeNormal
                                        color: Theme.textSecondary                 // FIX: de-emphasise volume
                                        Layout.preferredWidth: 160
                                        Layout.alignment: Qt.AlignVCenter
                                        horizontalAlignment: Text.AlignRight
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
