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

  property var assetFolder : "null"

  ColumnLayout {
    id: horizontalLayout
    anchors.fill: parent

    ListView {
        width: 200; height: 400

        XmlListModel {
            id: xmlModel
            source: "http://www.mysite.com/feed.xml"
            query: "/rss/channel/item"

            XmlRole { name: "title"; query: "title/string()" }
        }

        Component {
            id: xmlDelegate
            Text { text: title }
        }

        model: xmlModel
        delegate: xmlDelegate
    }
  }
}
