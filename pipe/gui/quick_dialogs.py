try:
	from PySide import QtGui as QtWidgets
	from PySide import QtGui as QtGui
	from PySide import QtCore
except ImportError:
	from PySide2 import QtWidgets, QtGui, QtCore

def error(errMsg, details=None, title='Error'):
	'''
	Reports a critical error
	'''
	message(errMsg, details=details, title=title)

def warning(warnMsg, details=None, title='Warning'):
	'''
	Reports a non-critical warning
	'''
	message(warnMsg, details=details, title=title)

def message(msg=' ', details=None, title='Message'):
	'''Reports a message'''
	print(msg)

	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(msg))
	if title == 'Warning':
		msgBox.setIcon(QtWidgets.QMessageBox.Warning)
	elif title == 'Error':
		msgBox.setIcon(QtWidgets.QMessageBox.Critical)
	else:
		msgBox.setIcon(QtWidgets.QMessageBox.Information)
	msgBox.setWindowTitle(title)
	msgBox.addButton(QtWidgets.QMessageBox.Ok)

	if details is not None:
		msgBox.setDetailedText(str(details))

	msgBox.exec_()

def info(infoMsg, title='Info'):
	'''Reports an informational message'''
	message(msg=infoMsg, title=title)

def light_error(errMsg, title='Warning'):
	'''Reports an error that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	return yes_or_no(errMsg, title=title)

def yes_or_no(question, details=None, title='Question'):
	'''Asks a question that can be resolved with a yes or no'''
	'''returns True if yes, otherwise False'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(question))
	msgBox.setWindowTitle(title)
	if title == 'Question':
		msgBox.setIcon(QtWidgets.QMessageBox.Question)
	else:
		msgBox.setIcon(QtWidgets.QMessageBox.Warning)
	noButton = msgBox.addButton(QtWidgets.QMessageBox.No)
	yesButton = msgBox.addButton(QtWidgets.QMessageBox.Yes)

	if details is not None:
		msgBox.setDetailedText(details)

	msgBox.exec_()

	if msgBox.clickedButton() == yesButton:
		return True
	elif msgBox.clickedButton() == noButton:
		return False

def input(label, title='Input', text=None):
	'''
	Allows the user to respond with a text input
	If the okay button is pressed it returns the inputed text, otherwise None
	'''
	dialog = QtWidgets.QInputDialog()
	text = dialog.getText(None, title, label, text=text)

	if text[1]:
		return text[0]
	else:
		return None

'''
	Have to use this instead of input in houdini to avoid black text on black bar
'''
class HoudiniInput(QtWidgets.QWidget):
    '''
    submitted is a class variable that must be instantiated outside of __init__
    in order for the Signal to be created correctly.
    '''
    submitted = QtCore.Signal(list)

    def __init__(self, parent=None, title="Enter info", width=350, height=75):
        super(HoudiniInput, self).__init__()
        if parent:
            self.parent = parent

        self.setWindowTitle(title)
        self.setObjectName('HoudiniInput')
        self.resize(width,height)
        self.initializeVBox()
        self.setLayout(self.vbox)
        self.show()

    def initializeVBox(self):
        self.vbox = QtWidgets.QVBoxLayout()
        self.initializeTextBar()
        self.initializeSubmitButton()

    def initializeTextBar(self):
		hbox = QtWidgets.QHBoxLayout()
		self.text_input = QtWidgets.QLineEdit()
		self.text_input.setStyleSheet("color: white; selection-color: black; selection-background-color: white;")
		self.text_input.textEdited.connect(self.textEdited)
		self.text_input.setFocus()
		hbox.addWidget(self.text_input)
		self.vbox.addLayout(hbox)

    def initializeSubmitButton(self):
		# Create the button widget
		self.button = QtWidgets.QPushButton("Confirm")
		self.button.setDefault(True)
		self.button.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Minimum)
		self.button.clicked.connect(self.submit)
		self.button.setEnabled(False)
		self.vbox.addWidget(self.button)

    def textEdited(self, newText):
		if len(newText) > 0:
			self.button.setEnabled(True)
			self.button.setDefault(True)
		else:
			self.button.setEnabled(False)

		self.values = newText

    '''
    	Send the selected values to a function set up in the calling class and
    	close the window. Use connect() on submitted to set up the receiving func.
    '''
    def submit(self):
		print(self.values)
		self.submitted.emit(self.values)
		self.close()

def large_input(label, title='Input', text=None):
	'''
	Allows the user to respond with a larger text input
	If the okay button is pressed it returns the inputed text, otherwise None
	'''

	dialog = QtWidgets.QTextEdit()
	# dialog.setCancelButtonText("Skip")toPlainText
	text = dialog.toPlainText(None, title, label, text=text)

	if text[1]:
		return text[0]
	else:
		return None

def binary_option(text, optionOne, optionTwo, title='Question'):
	'''Gives the user a message and a binary choice'''
	'''returns True if option one is selected, false if the second option is selected, otherwise None'''
	msgBox = QtWidgets.QMessageBox()
	msgBox.setText(msgBox.tr(text))
	msgBox.setIcon(QtWidgets.QMessageBox.Question)
	msgBox.setWindowTitle(title)
	fristButton = msgBox.addButton(msgBox.tr(optionOne), QtWidgets.QMessageBox.ActionRole)
	secondButton = msgBox.addButton(msgBox.tr(optionTwo), QtWidgets.QMessageBox.ActionRole)
	cancelButton = msgBox.addButton(QtWidgets.QMessageBox.Cancel)

	msgBox.exec_()

	if msgBox.clickedButton() == fristButton:
		return True
	elif msgBox.clickedButton() == secondButton:
		return False
	return None

def save(text):
	'''Prompts the user to save'''
	'''returns True if save is selected, False if don't save is selected otherwise None'''
	return binary_option(text, 'Save', 'Don\'t Save', title='Save Changes')
