try:
    from PySide import QtGui as QtWidgets
except ImportError:
    from PySide2 import QtWidgets

import pipe.gui as gui
from pipe.gui.write_message import WriteMessage

def TestInput(tool):

    TestInputDialog = WriteMessage(
        title="Please enter a string:"
    )

    TestInputDialog.exec_()

    if TestInputDialog.result() == QtWidgets.QDialog.Accepted:
        tool.finished(message=TestInputDialog.submitted)
    else:
        tool.finished(cancelled=True)
