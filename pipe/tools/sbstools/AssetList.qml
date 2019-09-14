import QtQuick.XmlListModel 2.0
import QtQuick 2.7
import QtQuick.Window 2.2
import QtQuick.Layouts 1.3
import QtQuick.Controls 2.0
import AlgWidgets 2.0
import AlgWidgets.Style 2.0
import "."


AlgWindow {
  property var windowTitle : "null"
  property var xmlFile : "null"
  property var action : "null"
  property var mediaDir : "null"

  id: window
  title: windowTitle
  visible: false
  minimumWidth: 600
  maximumWidth: minimumWidth
  minimumHeight: 500
  maximumHeight: minimumHeight

  flags: Qt.Window
		| Qt.WindowTitleHint // title
		| Qt.WindowSystemMenuHint // Recquired to add buttons
		| Qt.WindowMinMaxButtonsHint // minimize and maximize button
		| Qt.WindowCloseButtonHint // close button

  ColumnLayout {
    id: horizontalLayout
    anchors.fill: parent

    AlgScrollView {
      id: scrollArea
      anchors.fill: parent
      anchors.margins: 4
      maximumFlickVelocity: 1500
      contentHeight: 500


      ListView {
        width: 200; height: 400
        id: assetList
        Layout.minimumHeight: contentHeight
        spacing: 2

        XmlListModel {
          id: xmlModel
          source: xmlFile
          query: "/channel/item"

          XmlRole { name: "title"; query: "string()" }
        }

        model: xmlModel
        delegate: Rectangle {
          width: scrollArea.viewportWidth
          height: 25
          radius: 5
          border.color: AlgStyle.colors.gray(10)
          border.width: 1
          color: AlgStyle.colors.gray(15)
          Layout.leftMargin: 4
          Layout.rightMargin: 4
          Layout.topMargin: 4

          RowLayout {
            spacing: 2
            Layout.leftMargin: 4
            Layout.rightMargin: 4
            Layout.topMargin: 4
            Layout.alignment: Qt.AlignRight | Qt.AlignVCenter

            AlgLabel {
              text: title
              verticalAlignment: Text.AlignVCenter
              Layout.leftMargin: 4
              Layout.rightMargin: 4
              Layout.preferredWidth: 470
            }

            AlgButton {

              background: Rectangle {
                radius: 2
                border.color: AlgStyle.colors.gray(10)
                border.width: 1
                color: AlgStyle.colors.gray(20)
                anchors.rightMargin: 4
                anchors.verticalCenter: parent.verticalCenter
              }

              anchors.verticalCenter: parent.verticalCenter
              Layout.preferredWidth: 80
              anchors.rightMargin: 4
              text: "Select"
              enabled: true

              onClicked: {
                callAction(title, action, mediaDir)
              }
            }

          }

          // end delegate
        }
      }
    }
  }

  function callAction(assetName, action, mediaDir) {
    // check if files exist:
    if (alg.fileIO.exists("filepath")) {
      // we good
    }

    // may need to convert file to URL with alg.fileIO.localFileToUrl(path)

    if (action === "save") {
      save(assetName, mediaDir)
    } else if (action === "load") {
      load(assetName, mediaDir)
    } else if (action === "import") {
      importFile(assetName, mediaDir)
    } else if (action === "export") {
      exportMaps(assetName, mediaDir)
    } else {
      // Error
    }
  }

  function save(assetName, mediaDir) {
    alg.log.info(assetName)
    alg.log.info("save")
    alg.log.info(mediaDir)


    alg.project.save("file:///c:/Documents/project.spp", alg.project.SaveMode.Incremental)

  }

  function load(assetName, mediaDir) {
    alg.log.info(assetName)
    alg.log.info("load")
    alg.log.info(mediaDir)

  //  if alg.project.isOpen() {
  //    alg.project.close()
  //  }

    alg.project.open("filepath")
  }

  function importFile(assetName, mediaDir) {
    alg.log.info(assetName)
    alg.log.info("import")
    alg.log.info(mediaDir)

    alg.project.create("meshFile")
  }

  function exportMaps(assetName, mediaDir) {
    alg.log.info(assetName)
    alg.log.info("export")
    alg.log.info(mediaDir)

    // file:///opt/Allegorithmic/Substance_Painter/resources/javascript-doc/alg.mapexport.html#.save__anchor

  }

}
