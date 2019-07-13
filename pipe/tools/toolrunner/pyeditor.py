import sys
from os import path

from Qt.QtWidgets import QPlainTextEdit
from Qt.QtGui import QFontDatabase

from python_highlighter import PyStyle, PythonHighlighter

from PySide2 import QtWidgets, QtCore, QtGui
from Qt.QtWidgets import QPlainTextEdit
import itertools
from repr import repr

class PyLine:
    def __init__(self, cursor):
        self.linenum = cursor.blockNumber()
        self.text = cursor.block().text()
        self.spaces = sum( 1 for _ in itertools.takewhile(str.isspace, self.text.encode('utf-8')) if _ == ' ' )
        self.tabs = sum( 1 for _ in itertools.takewhile(str.isspace, self.text.encode('utf-8')) if _ == '\t' )
        self.indent = self.spaces // 4

    def __eq__(self, other):
        return self.text == other.text and self.linenum == other.linenum

class PyEditor(QPlainTextEdit):
    def __init__(self, settings):
        super(PyEditor, self).__init__()

        pystylesheet = path.join(settings.directory,
                                 settings.get_pystylesheet())
        pystyle = PyStyle(pystylesheet)

        document = self.document()
        document.setDefaultFont(
            QFontDatabase.systemFont(QFontDatabase.FixedFont))
        document.setDocumentMargin(5)
        highlight = PythonHighlighter(document, pystyle)

        self.installEventFilter(self)
        self.textChanged.connect(self.examineTextChanged)
        self.ing = False
        self.oldLine = PyLine(self.textCursor())

    def examineTextChanged(self):
        if self.ing:
            self.ing = False
            return
        self.ing = True

        cursor = self.textCursor()
        self.newLine = PyLine(cursor)

        #print("Old line: {}".format(self.oldLine))
        #print("New line: {}".format(self.newLine))

        block = cursor.block()
        oldLength = len(block.text())
        oldPosition = cursor.position()

        # TODO: Refactor each if statement piece into an "indent" function
        # TODO: Make it look at the previous linenumber for it's indent
        # TODO: Implement back tab
        # TODO: Implement select multiple lines and tab / back_tab
        cursor.beginEditBlock()
        if self.newLine.tabs > 0:
            block = cursor.block()
            cursor.setPosition(block.position())
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            if self.newLine.linenum > 0:
                cursor.insertText('\n')
            cursor.insertText(' ' * (self.newLine.spaces + (4 * self.newLine.tabs)))
            cursor.insertText(self.newLine.text.lstrip())
            self.newLine = PyLine(cursor)

        if self.oldLine.spaces > self.newLine.spaces and self.newLine.spaces % 4 > 0:
            block = cursor.block()
            cursor.setPosition(block.position())
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            if self.newLine.linenum > 0:
                cursor.insertText('\n')
            cursor.insertText(' ' * (self.newLine.indent * 4))
            cursor.insertText(self.newLine.text.lstrip())
            self.newLine = PyLine(cursor)

        if self.oldLine.linenum < self.newLine.linenum:
            block = cursor.block()
            cursor.setPosition(block.position())
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(' ' * 4 * self.oldLine.indent)
            stripped = self.oldLine.text.replace(' ', '').replace('\t', '')
            first = stripped.split("#")[0]
            if len(first) > 0 and first[-1] == ':':
                cursor.insertText(' ' * 4)
            cursor.insertText(self.newLine.text.lstrip())
            self.newLine = PyLine(cursor)

        cursor.setPosition(oldPosition + len(block.text()) - oldLength)
        cursor.endEditBlock()
        self.oldLine = PyLine(cursor)

    def handleTest(self):
        tab = "    "
        cursor = self.textCursor()

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        cursor.setPosition(end)
        cursor.movePosition(cursor.EndOfLine)
        end = cursor.position()

        cursor.setPosition(start)
        cursor.movePosition(cursor.StartOfLine)
        start = cursor.position()
        print cursor.position(), end

        while cursor.position() < end:
            cursor.movePosition(cursor.StartOfLine)
            cursor.insertText(tab)
            end += len(tab)
            cursor.movePosition(cursor.EndOfLine)

    #https://stackoverflow.com/questions/20420072/use-keypressevent-to-catch-enter-or-return
    def eventFilter(self, widget, event):
        if (event.type() == QtCore.QEvent.KeyPress and
            widget is self):
            print("Key is {}".format(event.key()))
            key = event.key()
            if key == QtCore.Qt.Key_Backtab:
                self.handleTest()
            elif key == QtCore.Qt.Key_Enter:
                self.setText('enter')
            #return False
        return QtWidgets.QWidget.eventFilter(self, widget, event)
