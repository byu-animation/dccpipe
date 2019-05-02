# TODO: removing the next line to be able to load departments from a config file down the line. Once config is ready, load depts from there.
# from pipe.am.environment import Department
from pipe.gui.checkout_gui import CheckoutWindow
import pipe.gui.select_from_list as select_gui
import pipe.tools.maya.utils.utils as maya_utils
from pipe.am.project import Project

from PySide2 import QtWidgets
import maya.cmds as mc
import maya.OpenMayaUI as omu
import os


class MayaCloner:
	def __init__(self):
		self.maya_checkout_dialog = None
		pass

	def rollback(self):
		print("Rollin' Rollin' Rollin' (Back)")

	def clone(self, gui=True, file_path=None, asset_name='Temp'):
		if gui:
			self.go()
		else:
			# TODO: make this method work
			self.non_gui_open(file_path, asset_name)

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
		project = Project()
		asset_list = project.list_assets()
		asset_list = ['one', 'two']
		self.item_gui = select_gui.SelectFromList(l=asset_list, parent=maya_utils.maya_main_window())
		print(asset_list)
		# print(item_gui.list)

	# def go(self):
	# 	parent = maya_utils.maya_main_window()
	# 	# TODO: replace temp depts with actual options for departments (loaded from config file)
	# 	self.maya_checkout_dialog = CheckoutWindow(parent, ["temp_dept_1", "temp_dept_2"])
	# 	self.maya_checkout_dialog.finished.connect(self.open_file)
	# 	# if dialog.exec_():
	# 	#	 print self.result
