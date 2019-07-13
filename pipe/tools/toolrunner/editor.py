import sys
from Qt.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QHBoxLayout,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QTextEdit
)
from Qt import QtCore, QtGui
from os import path
from settings import ToolRunnerSettings
from pyeditor import PyEditor
from tool import Tool

class ToolEditor(QMainWindow):
    def __init__(self, settings, parent = None):
        super(ToolEditor, self).__init__(parent)

        self.settings = settings
        self.tool_file = self.settings.get_default_tool()
        self._load_tool(self.tool_file)

        layout = QHBoxLayout()
        bar = self.menuBar()
        file = bar.addMenu("File")
        file.addAction("New")
        file.addAction("Save")
        file.addAction("Quit")
        file = bar.addMenu("Execute")
        file.addAction( QAction("&From Beginning", self,
                shortcut= QtGui.QKeySequence.New,
                statusTip="Create a new file",
                triggered=self._execute_from_beginning))

        self.items = QDockWidget(self.tool.name, self)
        self.listWidget = QListWidget()
        for method in self.tool.methods:
            self.listWidget.addItem(method["name"])

        self.items.setWidget(self.listWidget)
        self.items.setFloating(False)

        self.setCentralWidget(self.editor)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.items)
        self.setLayout(layout)
        self.setWindowTitle("Tool Editor {0}".format(settings.get_version()))

    def _load_tool(self, tool_path):
        self.tool = Tool(tool_path, gui=True)
        module = self.tool.methods[0]["module"]
        pwd = path.dirname(path.dirname(path.realpath(__file__)))
        tool_path = path.join(pwd, *(tool_path.split(".") + ["tool.py"]))
        self._load_editor(tool_path)

    def _load_editor(self, file):
        ext = path.splitext(file)[1]
        if ext.lower() in [".py", ".json"]:
            self.editor = PyEditor(self.settings)
        else:
            self.editor = QPlainTextEdit()

        with open(file, "r") as f:
            self.editor.setPlainText(f.read())
            f.close()

    def _execute_from_beginning(self):
        self.tool = Tool(self.tool_file, gui=True)
        self.tool.run()

def main():
    app = QApplication(sys.argv)
    directory = path.dirname(path.abspath(__file__))
    settings = ToolRunnerSettings(directory)
    ex = ToolEditor(settings)
    ex.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
