try:
    from PySide import QtCore
    from PySide import QtGui
except:
    from PySide2 import QtCore
    from PySide2 import QtGui
    from PySide2 import QtWidgets


def get_main_window():
    try:
        return QtGui.QApplication.activeWindow()
    except:
        return QtWidgets.QApplication.activeWindow()
