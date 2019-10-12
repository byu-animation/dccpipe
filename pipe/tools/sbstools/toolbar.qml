import AlgWidgets 2.0
import AlgWidgets.Style 2.0
import QtQuick 2.7
import QtQuick.Controls 2.0
import "toolbar.js" as Toolbar
import "."

Row {

  // Necessary if a project is being saved for the first time
  AssetList {
    id: saveWindow
  }

  property var windowReference : null
  property var toolImage : "untitled.svg"
  property var tooltipMessage : "null"
  property var action : "null"
  property var mediaDir : "null"

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
        callAction(action, mediaDir)
    }
  }

  function callAction(action, mediaDir) {
    if (action === "save") {
        toolbarSave(mediaDir)
      }
    // For any action that does not take special considerations
    else {
        try {
          windowReference.visible = true
        }
        catch(err) {
          alg.log.exception(err)
        }
    }
  }

function toolbarSave(mediaDir) {
  if (!alg.project.isOpen()) {
    alg.log.info("No project opened to save")
    // Default project is open
  } else if (alg.project.name() === mediaDir.split("/").pop() ) {
    alg.log.info("Cannot save invalid project")
    // Is a valid project that has been saved in the past
  } else if (Toolbar.isValidProject(mediaDir)) {
    var assetName = Toolbar.getAssetName()
    Toolbar.save(assetName, mediaDir)
  } else {
      // See main.xml for what this is doing
      saveWindow.xmlFile = mediaDir + "/production/props_and_actors.xml"
      windowReference = saveWindow
      windowReference.action = action
      windowReference.mediaDir = mediaDir
      windowReference.windowTitle = "Choose an asset to save to"
      windowReference.visible = true
    }
  }

}
