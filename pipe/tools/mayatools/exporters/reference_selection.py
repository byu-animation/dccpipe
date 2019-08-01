from PySide2 import QtWidgets
from PySide2.QtWidgets import *

import maya.cmds as cmds
from pymel.core import *
import pymel.core as pm
import os
from pipe.am.environment import Environment, Department
from pipe.am.project import Project
from pipe.gui import quick_dialogs as qd
from pipe.tools.mayatools.utils.utils import *

WINDOW_WIDTH = 330
WINDOW_HEIGHT = 300

class AlembicExportDialog(QDialog):
	def __init__(self, parent=maya_main_window()):
	#def setup(self, parent):
		QDialog.__init__(self, parent)
		self.setWindowTitle('Select Objects for Export')
		self.setFixedSize(WINDOW_WIDTH, WINDOW_HEIGHT)
		self.create_layout()
		self.export_button.clicked.connect(self.export)
		self.cancel_button.clicked.connect(self.cancel)
		self.canceled = False
		self.successful = False
		self.create_export_list()

	def cancel(self):
		self.canceled = True
		self.close_dialog()

	def export(self):
		self.successful = True
		self.close_dialog()

	def create_layout(self):
		#Create the selected item list
		self.selection_list = QListWidget()
		self.selection_list.setSelectionMode(QAbstractItemView.ExtendedSelection);
		self.selection_list.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

		#Create Export Alembic and Cancel buttons
		self.export_button = QPushButton('Export Alembic')
		self.cancel_button = QPushButton('Cancel')

		#Create button layout
		button_layout = QHBoxLayout()
		button_layout.setSpacing(2)
		button_layout.addStretch()

		button_layout.addWidget(self.export_button)
		button_layout.addWidget(self.cancel_button)

		#Create main layout
		main_layout = QVBoxLayout()
		main_layout.setSpacing(2)
		main_layout.setMargin(2)
		main_layout.addWidget(self.selection_list)
		main_layout.addLayout(button_layout)

		self.setLayout(main_layout)

	def create_export_list(self):
		#Remove all items from the list before repopulating
		self.selection_list.clear()

		#Add the list to select from
		loadedRef = getLoadedReferences()

		for ref in loadedRef:
			item = QListWidgetItem(str(ref))
			item.setText(str(ref))
			self.selection_list.addItem(item)

		self.selection_list.sortItems()

	def getSelectedReferences(self):
		selectedReferences = []
		selectedItems = self.selection_list.selectedItems()
		print "HERE IS WHERE WE HAVE THE LIST OF SELECTED ITEMS: " + str(selectedItems)
		for item in selectedItems:
			print item.text()
			selectedReferences.append(item.text())
		print "Here are the references: ", selectedReferences
		return selectedReferences

	def close_dialog(self):
		self.close()

def getSelectedReferences():
	dialog = AlembicExportDialog()
	dialog.exec_()
	if dialog.canceled:
		return None
	return dialog.getSelectedReferences()

def getLoadedReferences():
	references = pm.ls(references=True)
	loaded=[]
	print "Loaded References: "
	for ref in references:
		print "Checking status of " + ref
		try:
			if ref.isLoaded():
				loaded.append(ref)
		except:
			print "Warning: " + ref + " was not associated with a reference file"
	return loaded
