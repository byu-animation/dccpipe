import QtQuick 2.7
import Painter 1.0

PainterPlugin {

  HelloWorld {
    id: window
  }

  Component.onCompleted: {
    //alg.log.info("Hello!")
    var qmlToolbar = alg.ui.addToolBarWidget("toolbar.qml")
    qmlToolbar.windowReference = window
  }
}
