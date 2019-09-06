import AlgWidgets 1.0
import QtQuick 2.7
import QtQuick.Layouts 1.3
import "."

AlgWindow {
  id: window
  title: "HelloWorld"
  visible: false
  minimumWidth: 600
  maximumWidth: minimumWidth
  minimumHeight: 500
  maximumHeight: minimumHeight

  property var itemList : null

  ColumnLayout {
    id: horizontalLayout
    anchors.fill: parent

    Rectangle {
      id: buttonBar
      anchors.left: parent.left
      anchors.right: parent.right

      RowLayout {
        anchors.fill: parent

        AlgLabel {
          id: buttonLabel
          font.pixelSize: 14
          font.bold: true

          text: "Press Me"
        }

        AlgButton {
          text: "Say Hello!"
          Layout.preferredWidth: 150

          onClicked: {
            alg.log.info("Hello World!")
          }
        }
      }
    }
  }
}
