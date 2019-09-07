import AlgWidgets 2.0
import AlgWidgets.Style 2.0
import QtQuick 2.7
import QtQuick.Controls 2.0
import "."

Row {
  property var windowReference : null
  property var toolImage : "untitled.svg"
  property var tooltipMessage : "null"

  spacing: 2
  padding: 0

  Button {
    id: rect
    width: 200
    height: 30
    hoverEnabled: true
    ToolTip.visible: hovered
    ToolTip.delay: 1000
    ToolTip.timeout: 3000
    ToolTip.text: qsTr(tooltipMessage)

    Rectangle {
      anchors.fill: parent
      color: rect.hovered ? AlgStyle.colors.gray(15) : AlgStyle.colors.gray(20)

      Image {
        anchors.fill: parent
        anchors.margins: 3
        source: toolImage
        fillMode: Image.PreserveAspectFit
        sourceSize.width: width
        sourceSize.height: height
        mipmap: true
      }
    }

    onClicked: {
      try {
        windowReference.visible = true
      }
      catch(err) {
        alg.log.exception(err)
      }
    }
  }
}
