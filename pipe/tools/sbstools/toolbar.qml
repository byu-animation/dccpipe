import AlgWidgets 1.0
import QtQuick 2.7
import QtQuick.Controls 2.0
import "."

Row {
  property var windowReference : null

  Button {
    id: rect
    width: 30
    height: 30
    hoverEnabled: true

    Rectangle {
      anchors.fill: parent
      color: rect.hovered ? "#424242" : "#141414"

      Image {
        anchors.fill: parent
        anchors.margins: 3
        source: "untitled.svg"
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
