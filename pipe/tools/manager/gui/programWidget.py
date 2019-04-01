#!/usr/bin/python
# -'''- coding: utf-8 -'''-

import sys
import os
import time
from random import randint
from PySide2 import QtCore, QtWidgets, QtGui
from PySide2.QtCore import Signal
from resources import *

import traceback

class ProgramImageButton(QtWidgets.QAbstractButton):
	def __init__(self, program, size, singleClick, doubleClick, selected, warning, shortcut, parent):
		super(ProgramImageButton, self).__init__(parent)

		pipelionLoc = os.environ["BYU_TOOLS_DIR"] + "/pipelion"
		self.program = program
		self.pixmap = QtGui.QPixmap(pipelionLoc + "/" + self.program.icon)
		self.warningImage = QtGui.QPixmap(pipelionLoc + "/icons/warning-icon.png")
		self.shortcutImage = QtGui.QPixmap(pipelionLoc + "/icons/shortcut-icon.png")

		self.singleClick = singleClick
		self.doubleClick = doubleClick
		self.lastClick = time.time()
		self.released.connect(self.click)

		self.selected = selected
		self.warning = warning
		self.shortcut = shortcut
		self.size = size
		self.border_size = 4
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
		self.setSizePolicy(sizePolicy)

		self.setStyleSheet("""
		.ProgramImageButton {
			border: """ + str(self.border_size) + """px solid green;
			border-radius: """ + str(int(self.size / 2)) + """px;
			background-color: rgb(255, 255, 255);
			}
		""")

	def paintEvent(self, event):
		painter = QtGui.QPainter(self)
		opt = QtWidgets.QStyleOption()
		opt.initFrom(self)
		imageLength = self.size - self.border_size*2
		if self.selected and not self.shortcut:
			self.style().drawPrimitive(QtWidgets.QStyle.PE_Widget, opt, painter, self)
		painter.drawPixmap(QtCore.QRect(self.border_size, self.border_size, imageLength, imageLength), self.pixmap)
		if self.selected:
			painter.setBrush(QtGui.QBrush(QtGui.QColor.fromRgb(0,255,0,100)))
			painter.setPen(QtGui.QColor.fromRgb(0,0,0,0))
			painter.drawEllipse(QtCore.QPoint(int(self.size/2),int(self.size/2)), imageLength/2+1, imageLength/2+1)
		if self.underMouse():
			painter.setBrush(QtGui.QBrush(QtGui.QColor.fromRgb(0,0,0,100)))
			painter.setPen(QtGui.QColor.fromRgb(0,0,0,0))
			painter.drawEllipse(QtCore.QPoint(int(self.size/2),int(self.size/2)), imageLength/2+1, imageLength/2+1)
		if self.warning:
			painter.drawPixmap(QtCore.QRect(0, 0, imageLength*0.4, imageLength*0.4), self.warningImage)
		if self.shortcut:
			shortcutSize = imageLength*0.3
			painter.drawPixmap(QtCore.QRect(self.size - shortcutSize, self.size - shortcutSize, shortcutSize, shortcutSize), self.shortcutImage)

	def enterEvent(self, event):
		self.update()

	def leaveEvent(self, event):
		self.update()

	def sizeHint(self):
		return QtCore.QSize(self.size, self.size)

	def setSelected(self, selected):
		self.selected = selected
		self.update()

	def getSelected(self):
		return self.selected

	def toggleSelected(self):
		self.selected = not self.selected
		self.update()

	def click(self):
		double = False
		if self.doubleClick:
			double = self.checkDoubleClick()
		if self.singleClick and not double:
			self.singleClick[0](self.singleClick[1])
		self.setSelected(True)

	def checkDoubleClick(self):
		if (time.time() - self.lastClick) < 0.25:
			self.doubleClick[0](self.doubleClick[1])
			return True
		self.lastClick = time.time()
		return False



class ProgramWidget(QtWidgets.QWidget):
	clickedOutside = Signal()

	def __init__(self, program, size, text, fontSize, singleClick=None, doubleClick=None, selected=False, warning=False, shortcut=False, parent=None):
		super(ProgramWidget, self).__init__()
		if shortcut:
			doubleClick = (program.runProgram, [])
		self.projectButton = ProgramImageButton(program, size, singleClick, doubleClick, selected, warning, shortcut, parent)
		self.text = QtWidgets.QLabel(text)
		self.text.setFont(QtGui.QFont("Arial",fontSize,QtGui.QFont.Bold))
		self.text.setAlignment(QtCore.Qt.AlignCenter)
		self.layout = QtWidgets.QVBoxLayout()
		self.layout.addWidget(self.projectButton)
		self.size = size
		if text:
			self.layout.addWidget(self.text)
		self.setLayout(self.layout)
		sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
		self.setSizePolicy(sizePolicy)
		#self.setFocusPolicy(QtCore.Qt.ClickFocus)

	def setSelected(self, selected):
		self.projectButton.setSelected(selected)
		if selected:
			self.setFocus(QtCore.Qt.MouseFocusReason)

	def getSelected(self):
		return self.projectButton.getSelected()

	def toggleSelected(self):
		self.projectButton.toggleSelected()

	def sizeHint(self):
		return QtCore.QSize(self.size, self.size)

	def focusOutEvent(self, event):
		if(self.getSelected()):
			self.setSelected(False)
			self.clickedOutside.emit()


class ProgramShelfWidget(QtWidgets.QWidget):
	selectedSet = Signal(int)

	def __init__(self, programs, iconSize, textSize, names=None, shortcuts=False):
		super(ProgramShelfWidget, self).__init__()
		self.programs = programs
		self.programWidgets = []
		self.layout = QtWidgets.QHBoxLayout()
		self.iconSize = iconSize
		self.textSize = textSize
		for i in range(len(programs)):
			name = programs[i].name
			if names:
				name = names[i]
			self.programWidgets.append(ProgramWidget(programs[i], iconSize, name, textSize, singleClick=(self.setSelected,i), doubleClick=(self.setSelected,i), warning=False, shortcut=shortcuts))
			self.layout.addWidget(self.programWidgets[i])
			self.programWidgets[i].clickedOutside.connect(self.clickedOutside)
		self.setLayout(self.layout)

	def updateProgramViews(self):
		for i in range(len(self.programWidgets)):
			self.programWidgets[i].setSelected(self.selectedProgram == i)

	def setSelected(self, index):
		self.selectedProgram = index
		self.updateProgramViews()
		self.selectedSet.emit(index)

	def clickedOutside(self):
		for i in range(len(self.programWidgets)):
			if self.programWidgets[i].getSelected():
				self.setSelected(i)
				return
		self.setSelected(-1)




def singleClickT(name):
	print("SINGLE CLICK: " + name)

def doubleClickT():
	print("DOUBLE CLICK")

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)

	programs = PipelionResources.programs()
	widget = ProgramShelfWidget(programs, 100, 14)
	widget.show()

	sys.exit(app.exec_())
