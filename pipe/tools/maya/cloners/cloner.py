# TODO: removing the next line to be able to load departments from a config file down the line. Once config is ready, load depts from there.
# from pipe.am.environment import Department
from pipe.gui.checkout_gui import CheckoutWindow
from PySide2 import QtWidgets
import maya.cmds as mc
import maya.OpenMayaUI as omu
import os


class MayaCloner:
	def __init__(self):
		self.maya_checkout_dialog = None
		pass

	def clone(self, gui=True, file_path=None, asset_name='Temp'):
		if gui:
			self.go()
		else:
			# TODO: make this method work
			self.non_gui_open(file_path, asset_name)

	'''
	:return: Maya's main window
	'''
	def maya_main_window(self):
		for widget in QtWidgets.qApp.topLevelWidgets():
			if widget.objectName() == 'MayaWindow':
				return widget

		raise RuntimeError('Could not find MayaWindow instance')

	def open_file(self):
		filepath = self.maya_checkout_dialog.result

		if filepath is not None:
			if not mc.file(q=True, sceneName=True) == '':
				mc.file(save=True, force=True) #save file

			if not os.path.exists(filepath):
				mc.file(new=True, force=True)
				mc.file(rename=filepath)
				mc.file(save=True, force=True)
				print "new file "+filepath
			else:
				mc.file(filepath, open=True, force=True)
				print "open file "+filepath

	def non_gui_open(self, filePath=None, assetName='Temp'):
		if filePath == None:
			print 'no file'
			return
		if os.path.exists(filePath):
			mc.file(filePath, open=True, force=True)
			print "open file " + assetName
		else:
			print 'Does not Exist: '+assetName

	def go(self):
		parent = self.maya_main_window()
		# TODO: replace temp depts with actual options for departments (loaded from config file)
		self.maya_checkout_dialog = CheckoutWindow(parent, ["temp_dept_1", "temp_dept_2"])
		self.maya_checkout_dialog.finished.connect(self.open_file)
		# if dialog.exec_():
		#	 print self.result
