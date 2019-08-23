# TODO: removing the next line to be able to load departments from a config file down the line. Once config is ready, load depts from there.
# from pipe.am.environment import Department
import pipe.gui.select_from_list as sfl
import pipe.gui.quick_dialogs as qd
from pipe.tools.mayatools.utils.utils import *
from pipe.tools.mayatools.publishers.publisher import MayaPublisher as Publisher
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
		self.item_gui = sfl.SelectFromList(l=asset_list, parent=maya_main_window(), title="Select an asset to clone")
		self.item_gui.submitted.connect(self.results)

	def get_element_option(self, type, body):
		element = None

		if type == AssetType.PROP:
			element = body.get_element("model")

		elif type == AssetType.ACTOR:
			response = qd.binary_option("Which department for " + str(body.get_name()) + "?", "model", "rig")
			if response:
				element = body.get_element("model")
			else:
				element = body.get_element("rig")

		elif type == AssetType.SET:
			element = body.get_element("model")

		elif type == AssetType.SHOT:
			response = qd.binary_option("Which department for " + str(body.get_name()) + "?", "model", "anim")
			if response:
				element = body.get_element("model")
			else:
				element = body.get_element("anim")

		print("element: ", element)

		return element

	def results(self, value):
		print("Final value: ", value[0])
		filename = value[0]

		project = Project()
		body = project.get_body(filename)
		type = body.get_type()
		element = self.get_element_option(type, body)

		self.publishes = element.list_publishes()
		print("publishes: ", self.publishes)

		if not self.publishes:
			qd.error("There have been no publishes for this department. Maybe you meant model?")
			self.results(value)
			return

		# make the list a list of strings, not tuples
		self.sanitized_publish_list = []
		for publish in self.publishes:
			path = publish[3]
			file_ext = path.split('.')[-1]
			if not file_ext == "mb":
				continue
			label = publish[0] + " " + publish[1] + " " + publish[2]
			self.sanitized_publish_list.append(label)

		self.item_gui = sfl.SelectFromList(l=self.sanitized_publish_list, parent=maya_main_window(), title="Select publish to clone")
		self.item_gui.submitted.connect(self.publish_selection_results)

	def publish_selection_results(self, value):

		selected_publish = None
		for item in self.sanitized_publish_list:
			if value[0] == item:
				selected_publish = item

		selected_scene_file = None
		for publish in self.publishes:
			label = publish[0] + " " + publish[1] + " " + publish[2]
			if label == selected_publish:
				selected_scene_file = publish[3]

		# selected_scene_file is the one that contains the scene file for the selected commit
		if selected_scene_file is not None:
			unsaved_changes = mc.file(q=True, modified=True)

			if unsaved_changes:
				response = qd.yes_or_no("You have unsaved changes for the current asset. Would you like to publish them before you clone?")
				if response:
					# instead of saving, publish.
					scene = mc.file(q=True, sceneName=True)
					dir_path = scene.split("assets/")
					print("dir path: ", dir_path)
					try:
						asset_path = dir_path[1].split("/")
					except:
						# scene path is stored in the user directory instead of assets. We can't get the asset name, so they must publish manually.
						qd.error("Publish failed. Please publish manually before cloning the new asset.")
						return
					asset_name = asset_path[0]
					# asset = Project().get_body(asset_name)
					self.publisher = Publisher()
					self.publisher.non_gui_publish(asset_name, "model")

			if not os.path.exists(selected_scene_file):
				mc.file(new=True, force=True)
				mc.file(rename=selected_scene_file)
				mc.file(save=True, force=True)
				print "New file: " + selected_scene_file
			else:
				mc.file(selected_scene_file, open=True, force=True)
				print "File opened: " + selected_scene_file
