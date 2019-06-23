# syntax.py
# Adapted from code here:
# https://wiki.python.org/moin/PyQt/Python%20syntax%20highlighting
# and here:
# https://bitbucket.org/birkenfeld/pygments-main/src/default/pygments/lexers/python.py
import sys
import os.path as path

from Qt.QtCore import QRegExp
from Qt.QtGui import QColor, QTextCharFormat, QFont, QSyntaxHighlighter, QFontDatabase
from Qt.QtWidgets import QApplication, QPlainTextEdit

import json

def textCharFormat(style):
    """Return a QTextCharFormat with the given attributes.
    """
    fg = next((x for x in style if x not in ["italic", "bold"]), None)
    bg = next((x for x in style if x not in [fg, "italic", "bold"]), None)

    _format = QTextCharFormat()

    _fg = QColor()
    _fg.setNamedColor(fg)
    _format.setForeground(_fg)

    if bg:
        _bg = QColor()
        _bg.setNamedColor(bg)
        _format.setBackground(_bg)

    if "bold" in style:
        _format.setFontWeight(QFont.Bold)
    if "italic" in style:
        _format.setFontItalic(True)

    return _format

class PyStyle:
    def __init__(self, path):
        with open(path, 'r') as f:
            stylesheet = json.load(f)
            for style in stylesheet:
                self.__dict__.update({
                        style : textCharFormat(stylesheet[style])
                    })

class PythonHighlighter (QSyntaxHighlighter):
    """Syntax highlighter for the Python language.
    """
    # Python keywords
    keywords = [
        'class', 'def', 'import', 'from', 'assert', 'break', 'continue', 'del',
        'elif', 'else', 'except', 'exec', 'finally', 'for', 'global', 'if',
        'lambda', 'pass', 'print', 'raise', 'return', 'try', 'while', 'yield',
        'yield from', 'as', 'with', 'in', 'is', 'and', 'or', 'not', 'None',
        'True', 'False'
    ]

    builtins = [
        '__import__', 'abs', 'all', 'any', 'apply', 'basestring', 'bin',
        'bool', 'buffer', 'bytearray', 'bytes', 'callable', 'chr', 'classmethod',
        'cmp', 'coerce', 'compile', 'complex', 'delattr', 'dict', 'dir', 'divmod',
        'enumerate', 'eval', 'execfile', 'exit', 'file', 'filter', 'float',
        'frozenset', 'getattr', 'globals', 'hasattr', 'hash', 'hex', 'id',
        'input', 'int', 'intern', 'isinstance', 'issubclass', 'iter', 'len',
        'list', 'locals', 'long', 'map', 'max', 'min', 'next', 'object',
        'oct', 'open', 'ord', 'pow', 'property', 'range', 'raw_input', 'reduce',
        'reload', 'repr', 'reversed', 'round', 'set', 'setattr', 'slice',
        'sorted', 'staticmethod', 'str', 'sum', 'super', 'tuple', 'type',
        'unichr', 'unicode', 'vars', 'xrange', 'zip',

        '__abs__', '__add__', '__aenter__', '__aexit__', '__aiter__', '__and__',
        '__anext__', '__await__', '__bool__', '__bytes__', '__call__',
        '__complex__', '__contains__', '__del__', '__delattr__', '__delete__',
        '__delitem__', '__dir__', '__divmod__', '__enter__', '__eq__', '__exit__',
        '__float__', '__floordiv__', '__format__', '__ge__', '__get__',
        '__getattr__', '__getattribute__', '__getitem__', '__gt__', '__hash__',
        '__iadd__', '__iand__', '__ifloordiv__', '__ilshift__', '__imatmul__',
        '__imod__', '__import__', '__imul__', '__index__', '__init__',
        '__instancecheck__', '__int__', '__invert__', '__ior__', '__ipow__',
        '__irshift__', '__isub__', '__iter__', '__itruediv__', '__ixor__',
        '__le__', '__len__', '__length_hint__', '__lshift__', '__lt__',
        '__matmul__', '__missing__', '__mod__', '__mul__', '__ne__', '__neg__',
        '__new__', '__next__', '__or__', '__pos__', '__pow__', '__prepare__',
        '__radd__', '__rand__', '__rdivmod__', '__repr__', '__reversed__',
        '__rfloordiv__', '__rlshift__', '__rmatmul__', '__rmod__', '__rmul__',
        '__ror__', '__round__', '__rpow__', '__rrshift__', '__rshift__',
        '__rsub__', '__rtruediv__', '__rxor__', '__set__', '__setattr__',
        '__setitem__', '__str__', '__sub__', '__subclasscheck__', '__truediv__',
        '__xor__',

        '__annotations__', '__bases__', '__class__', '__closure__', '__code__',
        '__defaults__', '__dict__', '__doc__', '__file__', '__func__',
        '__globals__', '__kwdefaults__', '__module__', '__mro__', '__name__',
        '__objclass__', '__qualname__', '__self__', '__slots__', '__weakref__'
    ]

    # Python operators
    operators = [
        '=',
        # Comparison
        '==', '!=', '<', '<=', '>', '>=',
        # Arithmetic
        '\+', '-', '\*', '/', '//', '\%', '\*\*',
        # In-place
        '\+=', '-=', '\*=', '/=', '\%=',
        # Bitwise
        '\^', '\|', '\&', '\~', '>>', '<<',
    ]

    # Python braces
    braces = [
        '\{', '\}', '\(', '\)', '\[', '\]',
    ]
    def __init__(self, document, pystyle):
        QSyntaxHighlighter.__init__(self, document)

        # Multi-line strings (expression, flag, style)
        # FIXME: The triple-quotes in these two lines will mess up the
        # syntax highlighting from this point onward
        self.tri_single = (QRegExp("'''"), 1, pystyle.DOC_COMMENT)
        self.tri_double = (QRegExp('"""'), 2, pystyle.DOC_COMMENT)

        rules = []

        # Keyword, operator, and brace rules
        rules += [(r'\b%s\b' % w, 0, pystyle.KEYWORD)
            for w in PythonHighlighter.keywords]
        rules += [(r'\b%s\b' % w, 0, pystyle.BUILTIN_NAME)
            for w in PythonHighlighter.builtins]
        rules += [(r'\bself\b', 0, pystyle.SELF_PARAMETER)]

        # All other rules
        rules += [

            (r'\\([\\abfnrtv"\']|\n|N\{.*?\}|u[a-fA-F0-9]{4}|'
             r'U[a-fA-F0-9]{8}|x[a-fA-F0-9]{2}|[0-7]{1,3})',
                0, pystyle.VALID_STRING_ESCAPE),

            # decorators
            (r'@\w+', 0, pystyle.DECORATOR),

            # 'def' followed by an identifier
            (r'\bdef\b\s*(\w+)', 1, pystyle.FUNC_DEFINITION),
            # 'class' followed by an identifier
            (r'\bclass\b\s*(\w+)', 1, pystyle.CLASS_DEFINITION),

            # Numeric literals
            (r'\b[+-]?[0-9]+[lL]?\b', 0, pystyle.NUMBER),
            (r'\b[+-]?0[xX][0-9A-Fa-f]+[lL]?\b', 0, pystyle.NUMBER),
            (r'\b[+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?\b', 0,
                pystyle.NUMBER),

            # Double-quoted string, possibly containing escape sequences
            (r'"[^"\\]*(\\.[^"\\]*)*"', 0, pystyle.STRING),
            # Single-quoted string, possibly containing escape sequences
            (r"'[^'\\]*(\\.[^'\\]*)*'", 0, pystyle.STRING),



            # TODO: Make this play nice with # in the middle of a string
            # From '#' until a newline
            (r'#[^\n]*', 0, pystyle.LINE_COMMENT),
        ]

        # Build a QRegExp for each pattern
        self.rules = [(QRegExp(pat), index, fmt)
            for (pat, index, fmt) in rules]


    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text.
        """
        # Do other syntax formatting
        for expression, nth, format in self.rules:
            index = expression.indexIn(text, 0)

            while index >= 0:
                # We actually want the index of the nth match
                index = expression.pos(nth)
                length = len(expression.cap(nth))
                self.setFormat(index, length, format)
                index = expression.indexIn(text, index + length)

        self.setCurrentBlockState(0)

        # Do multi-line strings
        in_multiline = self.match_multiline(text, *self.tri_single)
        if not in_multiline:
            in_multiline = self.match_multiline(text, *self.tri_double)


    def match_multiline(self, text, delimiter, in_state, style):
        """Do highlighting of multi-line strings. ``delimiter`` should be a
        ``QRegExp`` for triple-single-quotes or triple-double-quotes, and
        ``in_state`` should be a unique integer to represent the corresponding
        state changes when inside those strings. Returns True if we're still
        inside a multi-line string when this function is finished.
        """
        # If inside triple-single quotes, start at 0
        if self.previousBlockState() == in_state:
            start = 0
            add = 0
        # Otherwise, look for the delimiter on this line
        else:
            start = delimiter.indexIn(text)
            # Move past this match
            add = delimiter.matchedLength()

        # As long as there's a delimiter match on this line...
        while start >= 0:
            # Look for the ending delimiter
            end = delimiter.indexIn(text, start + add)
            # Ending delimiter on this line?
            if end >= add:
                length = end - start + add + delimiter.matchedLength()
                self.setCurrentBlockState(0)
            # No; multi-line string
            else:
                self.setCurrentBlockState(in_state)
                length = len(text) - start + add
            # Apply formatting
            self.setFormat(start, length, style)
            # Look for the next match
            start = delimiter.indexIn(text, start + length)

        # Return True if still inside a multi-line string, False otherwise
        if self.currentBlockState() == in_state:
            return True
        else:
            return False

class ToolEditorSettingNotFoundError(Exception):
    '''
    Raised when there is not a setting associated with a given key
    '''
    pass

class ToolEditorSettings:
    def __init__(self, directory):
        pwd = path.dirname(path.abspath(__file__))

        self.settings = {}
        with open(path.join(directory, "settings.json"), "r") as f:
            self.settings = json.load(f)

        self.preferences = {}
        try:
            with open(path.join(directory, "preferences.json"), "r") as f:
                self.preferences = json.load(f)
        except:
            print("No user preferences found.")

    def get(self, key):
        '''
        User settings override application defaults.
        '''
        if key in self.preferences and key in self.settings:
            return self.preferences[key]

        elif key in self.settings:
            return self.settings[key]

        else:
            raise ToolEditorSettingNotFoundError()

if __name__ == "__main__":
    app = QApplication([])
    directory = path.dirname(path.abspath(__file__))
    settings = ToolEditorSettings(directory)

    pystylesheet = path.join(directory, settings.get("PYSTYLESHEET"))
    pystyle = PyStyle(pystylesheet)

    editor = QPlainTextEdit()
    document = editor.document()
    document.setDefaultFont(QFontDatabase.systemFont(QFontDatabase.FixedFont))
    document.setDocumentMargin(10)
    highlight = PythonHighlighter(editor.document(), pystyle)
    editor.show()

    # Load syntax.py into the editor for demo purposes
    #infile = open('tooleditor.py', 'r')
    #editor.setPlainText(infile.read())

    app.exec_()
