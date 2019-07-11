# TODO: removing the next line to be able to load departments from a config file down the line. Once config is ready, load depts from there.
# from pipe.am.environment import Department
from pipe.gui.checkout_gui import CheckoutWindow
import pipe.gui.select_from_list as select_gui
import pipe.tools.mayatools.utils.utils as maya_utils
from pipe.am.project import Project
from pipe.am.body import Body
from pipe.am.element import Element

from PySide2 import QtWidgets
import maya.cmds as mc
import maya.OpenMayaUI as omu
import os


class MayaCloner:
	def __init__(self):
		self.maya_checkout_dialog = None

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
			print 'File does not exist: '+assetName

	def go(self):
		project = Project()
		asset_list = project.list_assets()
		# asset_list = ['one', 'two']
		self.item_gui = select_gui.SelectFromList(l=asset_list, parent=maya_utils.maya_main_window(), title="Select an asset to clone")
		self.item_gui.submitted.connect(self.results)

	def results(self, value):
		print("Final value: ", value[0])
		filename = value[0]

		project = Project()
		body = project.get_body(filename)

		element = body.get_element("model")

		filepath = body.get_filepath()

		publishes = element.list_publishes();
		print("publishes: ",publishes)
		print("path: ", filepath)

		# make the list a list of strings, not tuples
		sanitized_publish_list = []
		for publish in publishes:
			label = publish[0] + " " + publish[1] + " " + publish[2]
			sanitized_publish_list.append(label)

		self.item_gui = select_gui.SelectFromList(l=sanitized_publish_list, parent=maya_utils.maya_main_window(), title="Select publish to clone")
		self.item_gui.submitted.connect(self.publish_selection_results)

	def publish_selection_results(self, value):
		print("Final value after publish selection: ", value[0])

		# TODO: what needs to happen now is to turn the selected publish into the filepath for the actual publish and get the scene file
		# TODO: Currently, the returned value is the string of username, timestamp, and comment.
		# TODO: What I'm thinking is of adding another value to the publish tuple, which would be an ID. This isn't necessary since we
		# TODO: could just compare timestamps. But, we still need a way of associating the selected publish with the correct commit directory.

		if filepath is not None:
			if not mc.file(q=True, sceneName=True) == '':
				mc.file(save=True, force=True) #save file

			if not os.path.exists(filepath):
				mc.file(new=True, force=True)
				mc.file(rename=filepath)
				mc.file(save=True, force=True)
				print "New file: " + filepath
			else:
				mc.file(filepath, open=True, force=True)
				print "File opened: " + filepath
		# TODO do something with the selected value: Get the alembic or .mb file and open in Maya
