import sys
import os
try:
    from PySide import QtGui as QtWidgets
    from PySide import QtGui as QtGui
    from PySide import QtCore
    from PySide.QtCore import Slot
except ImportError:
    from PySide2 import QtWidgets, QtGui, QtCore
    from PySide2.QtCore import Slot

class PipelionApp(QtWidgets.QApplication):
    def __init__(self):
        super(PipelionApp, self).__init__(sys.argv)
        self.setStyleSheet('''
            QLabel#logo { padding: 10 }
            SideBarLink { background-color: #20282600; color: white; padding-top: 5; padding-bottom: 5; padding-left: 10; padding-right:10; margin: 0 }
            SideBarLink:hover { background-color: #677c77; color: white }
            SideBarLink#nested { background-color: #364441; color: white; padding-top: 5; padding-bottom: 5; padding-left: 20; padding-right:10; margin: 0 }
            SideBarLink#nested:hover { background-color: #677c77; color: white }
            QMainWindow { background-color: #2c3835 }
        ''')
