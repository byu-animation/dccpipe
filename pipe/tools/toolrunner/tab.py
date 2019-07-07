import sys
from PySide2 import QtWidgets, QtCore, QtGui
import itertools
from repr import repr

class QLineEditValidator(QtGui.QValidator):

    @classmethod
    def connect(cls, line_edit, fixup=lambda s: s, validate=None, **kwargs):
        line_edit.setValidator(cls(line_edit, fixup=fixup, validate=validate, **kwargs))

    def __init__(self, line_edit, fixup=lambda s: s, validate=None, **kwargs):
        super().__init__(**kwargs)
        self.line_edit, self._fixup, self._validate = line_edit, fixup, \
            (lambda s, p: fixup(s) == s) if validate is None else validate

    def validate(self, s, p):
        if self.line_edit.hasFocus():
            return QValidator.Acceptable
        return QValidator.Acceptable if self._validate(s, p) else QValidator.Invalid

    def fixup(self, s):
        self.line_edit.setText(self._fixup(s))

#text = QLineEdit()
#QLineEditValidator.connect(text, fixup=lambda s: s.replace(' ', '_'))
#QLineEditValidator.connect(text, fixup=lambda s: s.replace(' ', '_'),
    #validate=lambda s, p: not ' ' in s)

class QPyline:
    def __init__(self, cursor):
        self.linenum = cursor.blockNumber()
        self.text = cursor.block().text()
        self.spaces = sum( 1 for _ in itertools.takewhile(str.isspace, self.text.encode('utf-8')) if _ == ' ' )
        self.tabs = sum( 1 for _ in itertools.takewhile(str.isspace, self.text.encode('utf-8')) if _ == '\t' )
        self.indent = self.spaces // 4

    def __str__(self):
        result = ""
        result += "\tLinenum: {}".format(self.linenum)
        result += "\tText: {}".format(repr(self.text))
        result += "\tSpaces: {}".format(self.spaces)
        result += "\tTabs: {}".format(self.tabs)
        result += "\tIndent: {}".format(self.indent)
        return result

    def __eq__(self, other):
        return self.text == other.text and self.linenum == other.linenum


class Window(QtWidgets.QWidget):
    def __init__(self):
        QtWidgets.QWidget.__init__(self)
        layout = QtWidgets.QVBoxLayout(self)
        self.button = QtWidgets.QPushButton('Test')
        self.edit = QtWidgets.QTextEdit()
        #self.edit.installEventFilter(self)
        layout.addWidget(self.edit)
        layout.addWidget(self.button)
        self.button.clicked.connect(self.handleTest)
        #self.edit.cursorPositionChanged.connect(self.examineCursorPositionChanged)
        self.edit.textChanged.connect(self.examineTextChanged)
        self.editing = False
        self.oldLine = QPyline(self.edit.textCursor())

    def examineTextChanged(self):
        if self.editing:
            self.editing = False
            return
        self.editing = True

        cursor = self.edit.textCursor()
        self.newLine = QPyline(cursor)

        #print("Old line: {}".format(self.oldLine))
        #print("New line: {}".format(self.newLine))

        block = cursor.block()
        oldLength = len(block.text())
        oldPosition = cursor.position()

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
            self.newLine = QPyline(cursor)

        if self.oldLine.spaces > self.newLine.spaces and self.newLine.spaces % 4 > 0:
            block = cursor.block()
            cursor.setPosition(block.position())
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            if self.newLine.linenum > 0:
                cursor.insertText('\n')
            cursor.insertText(' ' * (self.newLine.indent * 4))
            cursor.insertText(self.newLine.text.lstrip())
            self.newLine = QPyline(cursor)

        if self.oldLine.linenum < self.newLine.linenum:
            block = cursor.block()
            cursor.setPosition(block.position())
            cursor.select(QtGui.QTextCursor.BlockUnderCursor)
            cursor.removeSelectedText()
            cursor.insertText(' ' * 4 * self.oldLine.indent)
            stripped = self.oldLine.text.replace(' ', '').replace('\t', '')
            first = stripped.split("#")[0]
            #print("stripped {0}".format(repr(stripped)))
            #print("first {0}".format(repr(first)))
            if len(first) > 0 and first[-1] == ':':
                cursor.insertText(' ' * 4)
            cursor.insertText(self.newLine.text.lstrip())
            self.newLine = QPyline(cursor)

        cursor.setPosition(oldPosition + len(block.text()) - oldLength)
        cursor.endEditBlock()
        self.oldLine = QPyline(cursor)

    def handleTest(self):
        tab = "    "
        cursor = self.edit.textCursor()

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
        pass
        if (event.type() == QtCore.QEvent.KeyPress and
            widget is self.edit):
            key = event.key()
            if key == QtCore.Qt.Key_Tab:
                self.handleTest()
            elif key == QtCore.Qt.Key_Enter:
                self.edit.setText('enter')
            #return False
        return QtWidgets.QWidget.eventFilter(self, widget, event)

if __name__ == '__main__':
    app =  QtWidgets.QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
