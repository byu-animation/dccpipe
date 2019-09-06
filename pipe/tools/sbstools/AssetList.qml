import QtQuick.XmlListModel 2.0
import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import AlgWidgets 2.0
import AlgWidgets.Style 2.0
import "."


AlgWindow {
  id: window
  title: "Select Asset"
  visible: false
  minimumWidth: 600
  maximumWidth: minimumWidth
  minimumHeight: 500
  maximumHeight: minimumHeight

  property var xmlFile : "null"
  flags: Qt.Window
		| Qt.WindowTitleHint // title
		| Qt.WindowSystemMenuHint // Recquired to add buttons
		| Qt.WindowMinMaxButtonsHint // minimize and maximize button
		| Qt.WindowCloseButtonHint // close button

  ColumnLayout {
    id: horizontalLayout
    anchors.fill: parent

    ListView {
        width: 200; height: 400
        id: assetList
        Layout.minimumHeight: 400

        XmlListModel {
            id: xmlModel
            source: xmlFile
            query: "/channel/item"

            XmlRole { name: "title"; query: "string()" }
        }

        Component {
            id: xmlDelegate
            Text { text: title }
        }

        model: xmlModel
        delegate: xmlDelegate
    }

    // Create the list view now

  }
}
