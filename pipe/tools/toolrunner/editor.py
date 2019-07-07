# syntax.py
# Adapted from code here:
# https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
# and here:
# https://bitbucket.org/birkenfeld/pygments-main/src/default/pygments/lexers/python.py
import os.path as path

from Qt.QtWidgets import QPlainTextEdit
from Qt.QtGui import QFontDatabase

from python_highlighter import PyStyle, PythonHighlighter

class ToolEditor(QPlainTextEdit):
    def __init__(self, settings):
        super(ToolEditor, self).__init__()

        pystylesheet = path.join(settings.directory,
                                 settings.get_pystylesheet())
        pystyle = PyStyle(pystylesheet)

        document = self.document()
        document.setDefaultFont(
            QFontDatabase.systemFont(QFontDatabase.FixedFont))
        document.setDocumentMargin(5)
        highlight = PythonHighlighter(document, pystyle)
