import QtQuick 2.7
import Painter 1.0

PainterPlugin {

  AssetList {
    id: window
  }

  Component.onCompleted: {
    // alg.log.info(Qt.application.arguments[1])
    var mediaDir = Qt.application.arguments[1]
    var iconDir = mediaDir + "/pipe/tools/_resources/"
    var assetDir = mediaDir + "/production/assets/"

    var assetXml = mediaDir + "/production/props_and_actors.xml"
    alg.log.info(assetXml)

    window.xmlFile = assetXml

    // possible alg.ui methods: addDockWidget, addToolBarWidget, addWidgetToPluginToolBar, clickButton
    var importTool = alg.ui.addToolBarWidget("toolbar.qml")
    importTool.windowReference = window
    importTool.toolImage = iconDir + "clone.png"
    importTool.tooltipMessage = "Bring in an asset to paint"

    var publishTool = alg.ui.addToolBarWidget("toolbar.qml")
    publishTool.windowReference = window
    publishTool.toolImage = iconDir + "publish.svg"
    publishTool.tooltipMessage = "Publish maps to asset"
  }
}
