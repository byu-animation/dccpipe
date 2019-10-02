try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore

from tool_widget import ToolWidget

class CheckBoxOptions(ToolWidget):

    options_dict = {}

    def __init__(self, parent=None, title="Checkbox Options", options=[], submit_text="Continue"):
        QtWidgets.QWidget.__init__(self)
        if parent:
            self.parent = parent
        self.setObjectName('CheckBoxOptions')
        self.setWindowTitle(title)
        self.resize(600,150)
        self.options = {}

        vbox = QtWidgets.QVBoxLayout()

        for option in options:
            self.options_dict[option] = True

            hbox = QtWidgets.QHBoxLayout()
            option_checkbox = QtWidgets.QCheckBox(option)
            option_checkbox.setChecked(True)
            self.options[option] = option_checkbox

            hbox.addWidget(option_checkbox)
            vbox.addLayout(hbox)

        self.button = QtWidgets.QPushButton(submit_text)
        self.button.clicked.connect(self.submit)
        vbox.addWidget(self.button)
        self.setLayout(vbox)
        self.show()

    def option_changed(self, option_key, is_checked):
        self.options_dict.update({option_key : is_checked})

    def submit(self):
        for option in self.options.items():

            if option[1].checkState():
                self.options_dict[option[0]] = True
            else:
                self.options_dict[option[0]] = False

        self.submitted.emit(self.options_dict)
        self.close()
